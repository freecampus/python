"""Build Google Colab notebooks from Quarto lesson sources.

The QMD files are the source of truth for the website. This script creates
matching ``.ipynb`` files under ``docs/_site/notebooks/lessons`` so published
pages can link to Colab notebooks on the ``gh-pages`` branch.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SOURCE_ROOT = Path("docs/lessons")
OUTPUT_ROOT = Path("docs/_site/notebooks/lessons")


@dataclass(frozen=True)
class FrontMatter:
    title: str
    body: str


def notebook_path_for(source: Path, source_root: Path = SOURCE_ROOT) -> Path:
    """Return the notebook path relative to ``docs/_site`` for a QMD file."""
    return Path("notebooks/lessons") / source.relative_to(source_root).with_suffix(
        ".ipynb"
    )


def parse_front_matter(text: str, fallback_title: str) -> FrontMatter:
    """Extract a title and body from a QMD document."""
    if not text.startswith("---"):
        return FrontMatter(title=fallback_title, body=text)

    parts = text.split("---", 2)
    if len(parts) < 3:
        return FrontMatter(title=fallback_title, body=text)

    yaml_text = parts[1]
    body = parts[2].lstrip("\n")
    title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', yaml_text, re.M)
    title = title_match.group(1).strip() if title_match else fallback_title
    return FrontMatter(title=title, body=body)


def public_qmd_files(source_root: Path = SOURCE_ROOT) -> list[Path]:
    """List public QMD lesson pages that should become notebooks."""
    return sorted(
        path
        for path in source_root.rglob("*.qmd")
        if "_includes" not in path.parts and path.name != "_lesson-template.qmd"
    )


def is_python_fence(info: str) -> bool:
    """Return True when a fenced block should become a notebook code cell."""
    normalized = info.strip().lower()
    return normalized == "python" or normalized.startswith("{python")


def clean_code(source: str) -> str:
    """Remove Quarto cell options that are useful for HTML but noisy in Colab."""
    lines = []
    for line in source.splitlines():
        if line.lstrip().startswith("#|"):
            continue
        lines.append(line.rstrip())
    return "\n".join(lines).strip("\n")


def convert_quarto_div_start(line: str) -> str | None:
    """Convert a small subset of Quarto div starts to notebook-friendly text."""
    if not line.startswith(":::"):
        return line
    title_match = re.search(r'title="([^"]+)"', line)
    if title_match:
        return f"> **{title_match.group(1)}**"
    if line.strip() == ":::":
        return ""
    return ""


def clean_markdown(markdown: str) -> str:
    """Remove website-only syntax from markdown notebook cells."""
    markdown = re.sub(
        r'<script type="application/json" '
        r'class="fcpython-ojs-quiz-config">.*?</script>',
        "",
        markdown,
        flags=re.S,
    )
    markdown = re.sub(r"\{\{<\s*include\s+[^>]+>\}\}", "", markdown)
    markdown = re.sub(r"<!--\s*/?fcpython-[^>]+-->", "", markdown)

    cleaned_lines = []
    for line in markdown.splitlines():
        converted = convert_quarto_div_start(line.strip())
        if converted is None:
            continue
        cleaned_lines.append(
            converted if line.strip().startswith(":::") else line.rstrip()
        )

    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def markdown_cell(source: str) -> dict[str, Any]:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code_cell(source: str) -> dict[str, Any]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(True),
    }


def split_qmd_cells(markdown: str) -> list[dict[str, Any]]:
    """Split QMD body into notebook markdown and code cells."""
    cells: list[dict[str, Any]] = []
    markdown_buffer: list[str] = []
    fence_info: str | None = None
    fence_buffer: list[str] = []

    def flush_markdown() -> None:
        text = clean_markdown("\n".join(markdown_buffer))
        markdown_buffer.clear()
        if text:
            cells.append(markdown_cell(text))

    def flush_fence() -> None:
        nonlocal fence_info
        info = fence_info or ""
        text = "\n".join(fence_buffer).strip("\n")
        fence_buffer.clear()
        if is_python_fence(info):
            code = clean_code(text)
            if code:
                cells.append(code_cell(code))
        else:
            fenced = f"```{info}\n{text}\n```".strip()
            markdown = clean_markdown(fenced)
            if markdown:
                cells.append(markdown_cell(markdown))
        fence_info = None

    for line in markdown.splitlines():
        if fence_info is None:
            if line.startswith("```"):
                flush_markdown()
                fence_info = line[3:].strip()
                fence_buffer = []
            else:
                markdown_buffer.append(line)
        else:
            if line.startswith("```"):
                flush_fence()
            else:
                fence_buffer.append(line)

    if fence_info is not None:
        # Preserve an unterminated fence as markdown rather than dropping content.
        markdown_buffer.append(f"```{fence_info}")
        markdown_buffer.extend(fence_buffer)
    flush_markdown()
    return cells


def qmd_to_notebook(source: Path, source_root: Path = SOURCE_ROOT) -> dict[str, Any]:
    """Convert one lesson QMD file to an in-memory notebook dictionary."""
    fallback_title = source.stem.replace("-", " ").title()
    parsed = parse_front_matter(source.read_text(), fallback_title)
    rel_source = source.relative_to(source_root).as_posix()
    intro = (
        f"# {parsed.title}\n\n"
        "This notebook was generated from the FreeCampus Python lesson source. "
        "Run cells from top to bottom, write predictions before execution, and "
        "change one thing at a time.\n\n"
        f"Source lesson: `{rel_source}`"
    )
    cells = [markdown_cell(intro), *split_qmd_cells(parsed.body)]
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def build_notebooks(
    source_root: Path = SOURCE_ROOT, output_root: Path = OUTPUT_ROOT
) -> list[Path]:
    """Build all public lesson notebooks and return written paths."""
    written: list[Path] = []
    for source in public_qmd_files(source_root):
        relative_notebook = notebook_path_for(source, source_root).relative_to(
            "notebooks/lessons"
        )
        output = output_root / relative_notebook
        output.parent.mkdir(parents=True, exist_ok=True)
        notebook = qmd_to_notebook(source, source_root)
        output.write_text(json.dumps(notebook, indent=2, ensure_ascii=False) + "\n")
        written.append(output)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()

    written = build_notebooks(args.source_root, args.output_root)
    print(f"Built {len(written)} Colab notebooks in {args.output_root}")


if __name__ == "__main__":
    main()
