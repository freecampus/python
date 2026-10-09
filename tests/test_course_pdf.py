"""Check that the offline edition preserves the canonical teaching material."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from pathlib import Path

import pytest

SCRIPT = Path("scripts/build_course_pdf.py")
spec = importlib.util.spec_from_file_location("course_pdf", SCRIPT)
assert spec and spec.loader
pdf = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = pdf
spec.loader.exec_module(pdf)


@pytest.fixture(scope="module", autouse=True)
def fonts() -> None:
    directory = Path(
        os.environ.get("PDF_FONT_DIRECTORY", "/usr/share/fonts/truetype/dejavu")
    )
    pdf.register_fonts(directory)


def test_book_sequence_matches_catalog_completion_records() -> None:
    _catalog, course, chapters = pdf.course_chapters()
    assert [c.metadata["lesson_id"] for c in chapters if c.kind == "lesson"] == (
        course["completion"]["lesson_ids"]
    )
    assert [c.metadata["challenge_id"] for c in chapters if c.kind == "challenge"] == [
        c["id"] for c in course["completion"]["challenges"]
    ]
    for unit in course["units"]:
        sequence = [c for c in chapters if c.unit == unit["number"]]
        assert sequence[0].kind == "overview"
        assert sequence[-1].kind == "challenge"
        assert sum(c.kind == "lesson" for c in sequence) == unit["lesson_count"]


def test_printable_checkpoints_keep_all_options_and_answer_explanations() -> None:
    _catalog, _course, chapters = pdf.course_chapters()
    for chapter in chapters:
        answers: list[dict] = []
        prepared = pdf.prepare_markdown(chapter, answers)
        original = [json.loads(m) for m in pdf.QUIZ_RE.findall(chapter.body)]
        assert [a["quiz"] for a in answers] == original
        assert "fcpython-ojs-quiz-config" not in prepared
        assert "{{< include" not in prepared
        for quiz in original:
            for question in quiz["questions"]:
                assert question["prompt"] in prepared
                for option in question["options"]:
                    assert option in prepared
                assert 0 <= question["answer_index"] < len(question["options"])
                assert question["explanation"]


def test_all_course_diagrams_have_a_print_adapter() -> None:
    _catalog, _course, chapters = pdf.course_chapters()
    count = 0
    for chapter in chapters:
        for source in re.findall(r"```\{mermaid\}\n(.*?)```", chapter.body, re.S):
            drawing = pdf.diagram(source)
            assert drawing.width > 0 and drawing.height > 0
            count += 1
    assert count > 0
    with pytest.raises(ValueError, match="Unsupported diagram"):
        pdf.diagram("pie\n  Cats: 5")


def test_embedded_fonts_cover_the_entire_course_without_missing_glyph_boxes() -> None:
    _catalog, _course, chapters = pdf.course_chapters()
    characters = {char for c in chapters for char in c.body if ord(char) >= 32}
    pdf.safe_text("".join(sorted(characters)))
    pdf.safe_text("東京へようこそ 🌙 🚀", "Mono")
    with pytest.raises(ValueError, match="No embedded font"):
        pdf.safe_text("\U00010fff")


def test_partial_preview_cannot_replace_the_published_download(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="partial preview"):
        pdf.build(pdf.DOCS / "_site/downloads/python-foundations.pdf", tmp_path, 1)
