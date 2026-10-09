"""Build the Foundations study book from the canonical QMD sources.

No lesson code or browser JavaScript is executed. Pandoc parses Markdown;
ReportLab supplies paginated typography, printable checkpoints, vector diagrams,
bookmarks, a linked contents section, and an answer key.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import yaml
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.graphics.svgpath import SvgPath
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = "https://freecampus.org/python/"
WIDTH, HEIGHT = A4
MARGIN = 52
TEXT_WIDTH = WIDTH - MARGIN * 2
INK = colors.HexColor("#172033")
VIOLET = colors.HexColor("#5753d9")
MUTED = colors.HexColor("#596579")
PAPER = colors.HexColor("#fbfaf7")
BORDER = colors.HexColor("#dedee6")
QUIZ_RE = re.compile(
    r'<script\s+type="application/json"\s+class="fcpython-ojs-quiz-config">(.*?)</script>',
    re.S,
)


@dataclass
class Chapter:
    source: Path
    title: str
    unit: int
    kind: str
    key: str
    body: str
    metadata: dict[str, Any]


def front_matter(source: Path) -> tuple[dict[str, Any], str]:
    parts = source.read_text().split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"Missing front matter: {source}")
    return yaml.safe_load(parts[1]), parts[2]


def course_chapters() -> tuple[dict[str, Any], dict[str, Any], list[Chapter]]:
    catalog = yaml.safe_load((DOCS / "courses/_catalog.yml").read_text())
    course = next(c for c in catalog["courses"] if c["id"] == "python-foundations")
    chapters = []
    for unit in course["units"]:
        directory = DOCS / unit["directory"]
        lessons = []
        for source in directory.glob("*.qmd"):
            metadata, body = front_matter(source)
            if metadata.get("lesson_id"):
                lessons.append((metadata["lesson_order"], source, metadata, body))
        lessons.sort(key=lambda item: item[0])
        if len(lessons) != unit["lesson_count"]:
            raise ValueError(f"Catalog lesson count mismatch: {unit['id']}")
        ordered = [(directory / "index.qmd", "overview")]
        ordered += [(source, "lesson") for _, source, _, _ in lessons]
        ordered += [(directory / "challenge.qmd", "challenge")]
        for source, kind in ordered:
            metadata, body = front_matter(source)
            key = source.relative_to(DOCS).with_suffix("").as_posix()
            chapters.append(
                Chapter(
                    source, metadata["title"], unit["number"], kind, key, body, metadata
                )
            )
    if sum(c.kind == "lesson" for c in chapters) != course["lesson_count"]:
        raise ValueError("Course lesson count mismatch")
    return catalog, course, chapters


def prepare_markdown(chapter: Chapter, answers: list[dict[str, Any]]) -> str:
    """Convert web-only elements without dropping questions, hints, or solutions."""
    body = chapter.body

    def quiz(match: re.Match[str]) -> str:
        config = json.loads(match.group(1))
        answers.append({"chapter": chapter.key, "title": chapter.title, "quiz": config})
        lines = [f"\n### {config['title']}\n", config.get("instructions", "")]
        for number, q in enumerate(config["questions"], 1):
            lines.append(f"\n**{number}. {q['prompt']}**\n")
            for index, option in enumerate(q["options"]):
                lines.append(f"- **{chr(65 + index)}.** {option}")
        lines.append(
            "\nWrite your choices before checking the answer key at the end of "
            "this book.\n"
        )
        return "\n".join(lines)

    body = QUIZ_RE.sub(quiz, body)
    body = re.sub(r"\{\{<\s*include\s+[^>]+>\}\}", "", body)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r'<div class="fc-assessment-action".*?</div>', "", body, flags=re.S)
    body = re.sub(r"<summary>(.*?)</summary>", r"\n\n**\1**\n\n", body, flags=re.S)
    body = re.sub(r"</?details[^>]*>", "", body)
    # Quarto cell metadata is not learner code.
    body = re.sub(r"^\s*(?:#\||%%\|).*\n?", "", body, flags=re.M)
    body = re.sub(r"^```\{python[^}]*\}", "```python", body, flags=re.M)
    body = re.sub(r"^```\{mermaid\}", "```mermaid", body, flags=re.M)
    # Keep callout titles while letting Pandoc retain the contained Markdown.
    body = re.sub(r'^:::.*?title="([^"]+)".*$', r"\n**\1**\n", body, flags=re.M)
    return body


def markdown_ast(markdown: str) -> list[dict[str, Any]]:
    result = subprocess.run(
        ["quarto", "pandoc", "--from", "markdown-raw_tex", "--to", "json"],
        input=markdown,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)["blocks"]


def register_fonts(directory: Path) -> None:
    files = {
        "Book": "DejaVuSans.ttf",
        "BookBold": "DejaVuSans-Bold.ttf",
        "BookItalic": "DejaVuSans-Oblique.ttf",
        "Mono": "DejaVuSansMono.ttf",
    }
    for name, filename in files.items():
        path = directory / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing font {path}; install fonts-dejavu-core")
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily(
        "Book",
        normal="Book",
        bold="BookBold",
        italic="BookItalic",
        boldItalic="BookBold",
    )
    pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono", italic="Mono")
    pdfmetrics.registerFont(
        TTFont("Unicode", str(ROOT / "scripts/pdf/fonts/freecampus-unicode.ttf"))
    )
    pdfmetrics.registerFont(
        TTFont("Symbols", str(ROOT / "scripts/pdf/fonts/freecampus-symbols.ttf"))
    )
    for name in ["Unicode", "Symbols"]:
        pdfmetrics.registerFontFamily(
            name, normal=name, bold=name, italic=name, boldItalic=name
        )


def safe_text(text: str, base: str = "Book") -> str:
    """Use embedded fallback glyphs instead of silently printing missing boxes."""
    result = []
    for char in text:
        if char == "\n":
            result.append("<br/>")
            continue
        if ord(char) in pdfmetrics.getFont(base).face.charWidths:
            result.append(html.escape(char))
            continue
        for name in ["Book", "Unicode", "Symbols"]:
            if name in pdfmetrics.getRegisteredFontNames() and (
                ord(char) in pdfmetrics.getFont(name).face.charWidths
            ):
                result.append(f'<font name="{name}">{html.escape(char)}</font>')
                break
        else:
            raise ValueError(f"No embedded font for U+{ord(char):04X} {char!r}")
    return "".join(result)


def styles() -> dict[str, ParagraphStyle]:
    base = dict(
        fontName="Book",
        fontSize=9.5,
        leading=14.6,
        textColor=INK,
        spaceAfter=7,
        splitLongWords=True,
        allowWidows=0,
        allowOrphans=0,
    )
    normal = ParagraphStyle("body", **base)
    return {
        "body": normal,
        "small": ParagraphStyle(
            "small", parent=normal, fontSize=8, leading=11.5, textColor=MUTED
        ),
        "title": ParagraphStyle(
            "title",
            parent=normal,
            fontName="BookBold",
            fontSize=25,
            leading=31,
            spaceAfter=16,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=normal,
            fontName="BookBold",
            fontSize=14,
            leading=19,
            spaceBefore=15,
            spaceAfter=9,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "h3",
            parent=normal,
            fontName="BookBold",
            fontSize=11,
            leading=16,
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "h4": ParagraphStyle(
            "h4",
            parent=normal,
            fontName="BookBold",
            fontSize=9.5,
            leading=14,
            spaceBefore=9,
            keepWithNext=True,
        ),
        "code": ParagraphStyle(
            "code",
            fontName="Mono",
            fontSize=7.4,
            leading=10.4,
            textColor=INK,
            spaceAfter=0,
        ),
        "cell": ParagraphStyle(
            "cell", parent=normal, fontSize=8, leading=11.5, spaceAfter=0
        ),
    }


class CodeBlock(Flowable):
    """A splittable code panel; long source lines wrap with a continuation marker."""

    def __init__(self, source: str, language: str = "", lines: list[str] | None = None):
        super().__init__()
        self.source, self.language, self.lines = source, language, lines
        self.spaceBefore, self.spaceAfter = 5, 10

    def wrap(
        self, available_width: float, available_height: float
    ) -> tuple[float, float]:
        self.width = available_width
        if self.lines is None:
            columns = max(
                20,
                int((available_width - 22) / pdfmetrics.stringWidth("M", "Mono", 7.4)),
            )
            lines = []
            for source_line in self.source.splitlines() or [""]:
                # Spaces are preserved, including indentation and blank lines.
                while len(source_line) > columns:
                    lines.append(source_line[: columns - 2] + " ↪")
                    source_line = "    " + source_line[columns - 2 :]
                lines.append(source_line)
            self.lines = lines
        self.height = 25 + len(self.lines) * 10.4
        return self.width, self.height

    def split(self, available_width: float, available_height: float) -> list[Flowable]:
        self.wrap(available_width, available_height)
        count = int((available_height - 25) / 10.4)
        if count < 2:
            return []
        assert self.lines is not None
        return [
            CodeBlock("", self.language, self.lines[:count]),
            CodeBlock("", f"{self.language} (continued)", self.lines[count:]),
        ]

    def draw(self) -> None:
        canvas = self.canv
        canvas.setFillColor(colors.HexColor("#f3f3f8"))
        canvas.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=0)
        canvas.setFillColor(MUTED)
        canvas.setFont("Book", 6.5)
        canvas.drawString(10, self.height - 12, self.language.upper() or "TEXT")
        for index, line in enumerate(self.lines or []):
            # Paragraph supports CJK fallback and preserves code spaces via NBSP.
            text = safe_text(line.replace(" ", "\u00a0"), "Mono")
            paragraph = Paragraph(text or "&#160;", styles()["code"])
            paragraph.wrap(self.width - 20, 11)
            paragraph.drawOn(canvas, 10, self.height - 27 - index * 10.4)


def diagram(source: str) -> Drawing:
    """Lay out the course's bounded Mermaid subset as portable vector diagrams.

    Parsing is deliberately strict: future unsupported diagram syntax must fail
    the build rather than quietly disappear from the book.
    """
    lines = [
        line.strip()
        for line in source.splitlines()
        if line.strip() and not line.startswith("%%")
    ]
    if not lines:
        raise ValueError("Empty diagram")
    if lines[0] == "sequenceDiagram":
        participants = {}
        messages = []
        for line in lines[1:]:
            match = re.fullmatch(r"participant (\w+) as (.+)", line)
            if match:
                participants[match[1]] = match[2]
                continue
            match = re.fullmatch(r"(\w+)(--?>>)(\w+): (.+)", line)
            if not match:
                raise ValueError(f"Unsupported sequence diagram line: {line}")
            messages.append(match.groups())
        drawing = Drawing(TEXT_WIDTH, 70 + len(messages) * 36)
        names = list(participants)
        x = {
            name: 45 + index * (TEXT_WIDTH - 90) / max(1, len(names) - 1)
            for index, name in enumerate(names)
        }
        for name, label in participants.items():
            drawing.add(
                String(
                    x[name],
                    drawing.height - 15,
                    label,
                    textAnchor="middle",
                    fontName="BookBold",
                    fontSize=9,
                    fillColor=INK,
                )
            )
            drawing.add(
                Line(
                    x[name],
                    12,
                    x[name],
                    drawing.height - 25,
                    strokeColor=BORDER,
                    strokeDashArray=[3, 3],
                )
            )
        for i, (left, arrow, right, label) in enumerate(messages):
            y = drawing.height - 48 - i * 36
            a, b = x[left], x[right]
            if a == b:
                drawing.add(Line(a, y, a + 26, y, strokeColor=VIOLET))
                drawing.add(Line(a + 26, y, a + 26, y - 13, strokeColor=VIOLET))
                drawing.add(Line(a + 26, y - 13, a, y - 13, strokeColor=VIOLET))
                drawing.add(String(a + 5, y + 6, label, fontName="Book", fontSize=7.5))
            else:
                drawing.add(
                    Line(
                        a,
                        y,
                        b,
                        y,
                        strokeColor=VIOLET,
                        strokeDashArray=[3, 2] if arrow.startswith("--") else None,
                    )
                )
                sign = 1 if b > a else -1
                drawing.add(
                    Polygon(
                        [b, y, b - sign * 6, y + 3, b - sign * 6, y - 3],
                        fillColor=VIOLET,
                        strokeColor=VIOLET,
                    )
                )
                drawing.add(
                    String(
                        (a + b) / 2,
                        y + 7,
                        label,
                        textAnchor="middle",
                        fontName="Book",
                        fontSize=7.5,
                        fillColor=INK,
                    )
                )
        return drawing
    state = lines[0] == "stateDiagram-v2"
    if not state and not lines[0].startswith("flowchart "):
        raise ValueError(f"Unsupported diagram: {lines[0]}")
    nodes: dict[str, tuple[str, str]] = {}
    edges: list[tuple[str, str, str]] = []
    token = (
        r'(\[\*\]|[A-Za-z_]\w*)(?:\[("(?:[^"\\]|\\.)*"|[^\]]*)\]|'
        r'\{("(?:[^"\\]|\\.)*"|[^}]*)\})?'
    )
    node_pattern = re.compile(token)
    arrow_pattern = re.compile(
        r"\s*(?:-->|-\.->)(?:\|([^|]+)\|)?\s*|\s*--\s+(.+?)\s+-->\s*|\s*-\.\s+(.+?)\s+\.->\s*"
    )

    def node(match: re.Match[str]) -> str:
        identity = match[1]
        label = (
            match[2] or match[3] or ("Start / end" if identity == "[*]" else identity)
        )
        label = html.unescape(
            label.strip('"').replace("<br/>", "\n").replace("<br>", "\n")
        )
        if identity not in nodes or match[2] or match[3]:
            nodes[identity] = (label, "diamond" if match[3] else "box")
        return identity

    for line in lines[1:]:
        if state:
            match = re.fullmatch(
                r"(\[\*\]|\w+)\s*-->\s*(\[\*\]|\w+)(?::\s*(.*))?", line
            )
            if not match:
                raise ValueError(f"Unsupported state line: {line}")
            left, right, label = match.groups()
            for name in [left, right]:
                nodes[name] = ("Start / end" if name == "[*]" else name, "box")
            edges.append((left, right, label or ""))
            continue
        first = node_pattern.match(line)
        if not first:
            raise ValueError(f"Unsupported diagram node: {line}")
        left, position = node(first), first.end()
        while position < len(line):
            arrow = arrow_pattern.match(line, position)
            if not arrow:
                raise ValueError(f"Unsupported diagram arrow: {line[position:]}")
            following = node_pattern.match(line, arrow.end())
            if not following:
                raise ValueError(f"Unsupported diagram target: {line}")
            right = node(following)
            label = next((x for x in arrow.groups() if x), "").strip('"')
            edges.append((left, right, label))
            left, position = right, following.end()
    # Breadth-first levels keep back edges from creating an infinite layout.
    incoming = {right for left, right, _ in edges if left != right}
    roots = [name for name in nodes if name not in incoming] or [next(iter(nodes))]
    levels = {name: 0 for name in roots}
    queue = list(roots)
    while queue:
        left = queue.pop(0)
        for a, b, _ in edges:
            if a == left and b not in levels:
                levels[b] = levels[left] + 1
                queue.append(b)
    for name in nodes:
        levels.setdefault(name, 0)
    groups = [
        [n for n in nodes if levels[n] == level]
        for level in sorted(set(levels.values()))
    ]
    # Use vertical layout for book-width legibility.
    row_height = 64
    height = len(groups) * row_height + 25
    drawing = Drawing(TEXT_WIDTH, height)
    positions = {}
    for row, group in enumerate(groups):
        for col, name in enumerate(group):
            x = (col + 0.5) * TEXT_WIDTH / len(group)
            y = height - 45 - row * row_height
            positions[name] = (x, y, min(160, TEXT_WIDTH / len(group) - 12), 44)
    for left, right, _label in edges:
        x1, y1, w1, h1 = positions[left]
        x2, y2, _w2, h2 = positions[right]
        if left == right or y2 >= y1:
            # Keep cycle labels visible outside the node; do not hide transitions.
            x = min(TEXT_WIDTH - 5, x1 + w1 / 2 + 8)
            drawing.add(Line(x1 + w1 / 2, y1, x, y1, strokeColor=VIOLET))
            drawing.add(Line(x, y1, x, y2 + h2 / 2 + 7, strokeColor=VIOLET))
            drawing.add(
                Line(x, y2 + h2 / 2 + 7, x2, y2 + h2 / 2 + 7, strokeColor=VIOLET)
            )
            a, b = x2, y2 + h2 / 2 + 7
            drawing.add(
                Polygon(
                    [a, b - 6, a - 3, b, a + 3, b], fillColor=VIOLET, strokeColor=VIOLET
                )
            )
        else:
            drawing.add(Line(x1, y1 - h1 / 2, x2, y2 + h2 / 2, strokeColor=VIOLET))
            drawing.add(
                Polygon(
                    [x2, y2 + h2 / 2, x2 - 3, y2 + h2 / 2 + 6, x2 + 3, y2 + h2 / 2 + 6],
                    fillColor=VIOLET,
                    strokeColor=VIOLET,
                )
            )
        # Full transition captions are reproduced in an accompanying legend.
    for name, (x, y, width, height) in positions.items():
        label, shape = nodes[name]
        if shape == "diamond":
            drawing.add(
                Polygon(
                    [
                        x,
                        y + height / 2,
                        x + width / 2,
                        y,
                        x,
                        y - height / 2,
                        x - width / 2,
                        y,
                    ],
                    fillColor=PAPER,
                    strokeColor=BORDER,
                )
            )
        else:
            drawing.add(
                Rect(
                    x - width / 2,
                    y - height / 2,
                    width,
                    height,
                    rx=4,
                    fillColor=PAPER,
                    strokeColor=BORDER,
                )
            )
        rows = [
            piece
            for line in label.splitlines()
            for piece in textwrap.wrap(line, max(8, int(width / 5))) or [""]
        ]
        for i, line in enumerate(rows):
            drawing.add(
                String(
                    x,
                    y + (len(rows) - 1) * 5 - i * 10,
                    line,
                    textAnchor="middle",
                    fontName="Book",
                    fontSize=8,
                    fillColor=INK,
                )
            )
    drawing._transitions = [
        (nodes[a][0].replace("\n", " / "), nodes[b][0].replace("\n", " / "), label)
        for a, b, label in edges
        if label
    ]
    return drawing


class BookRenderer:
    def __init__(self, chapter: Chapter, style: dict[str, ParagraphStyle]):
        self.chapter, self.style = chapter, style

    def inline(self, elements: list[dict[str, Any]]) -> str:
        output = []
        for element in elements:
            kind, content = element["t"], element.get("c")
            if kind == "Str":
                output.append(safe_text(content))
            elif kind in {"Space", "SoftBreak"}:
                output.append(" ")
            elif kind == "LineBreak":
                output.append("<br/>")
            elif kind == "Code":
                output.append(
                    f'<font name="Mono" size="8">{safe_text(content[1], "Mono")}</font>'
                )
            elif kind in {"Strong", "Emph", "Strikeout", "Superscript", "Subscript"}:
                tag = {
                    "Strong": "b",
                    "Emph": "i",
                    "Strikeout": "strike",
                    "Superscript": "super",
                    "Subscript": "sub",
                }[kind]
                output.append(f"<{tag}>{self.inline(content)}</{tag}>")
            elif kind in {"Span", "Cite"}:
                output.append(self.inline(content[1]))
            elif kind == "Quoted":
                output.append('"' + self.inline(content[1]) + '"')
            elif kind == "Link":
                label, destination = self.inline(content[1]), content[2][0]
                if not destination.startswith(("http:", "https:", "mailto:")):
                    source_url = SITE + self.chapter.source.relative_to(DOCS).as_posix()
                    destination = urljoin(source_url, destination).replace(
                        ".qmd", ".html"
                    )
                output.append(
                    f'<link href="{html.escape(destination, quote=True)}" '
                    f'color="#5753d9">{label}</link>'
                )
            elif kind == "Math":
                # The Foundations math is scientific notation, not general TeX.
                expression = content[1].replace(r"\times", "\u00d7")
                expression = re.sub(r"\^\{([^}]+)\}", r"<super>\1</super>", expression)
                expression = re.sub(r"\^(\d+)", r"<super>\1</super>", expression)
                if "\\" in expression:
                    raise ValueError(f"Unsupported math: {content[1]}")
                output.append(expression)
            elif kind == "Note":
                output.append(" (" + self.plain_blocks(content) + ")")
            elif kind == "RawInline":
                if content[0] == "html" and content[1] in {"<br>", "<br/>", "<br />"}:
                    output.append("<br/>")
                elif content[1].strip():
                    raise ValueError(f"Unsupported inline markup: {content}")
            elif kind == "Image":
                raise ValueError(f"Image requires a print adapter: {content}")
            else:
                raise ValueError(f"Unsupported inline: {kind}")
        return "".join(output)

    def plain_blocks(self, blocks: list[dict[str, Any]]) -> str:
        return "<br/>".join(
            self.inline(b["c"]) for b in blocks if b["t"] in {"Para", "Plain"}
        )

    def blocks(
        self, blocks: list[dict[str, Any]], cell: bool = False
    ) -> list[Flowable]:
        result: list[Flowable] = []
        for block in blocks:
            kind, content = block["t"], block.get("c")
            if kind in {"Para", "Plain"}:
                text = self.inline(content)
                if text.strip():
                    result.append(
                        Paragraph(text, self.style["cell" if cell else "body"])
                    )
            elif kind == "Header":
                level, _, text = content
                result.append(
                    Paragraph(
                        self.inline(text),
                        self.style[
                            "h2" if level <= 2 else "h3" if level == 3 else "h4"
                        ],
                    )
                )
            elif kind == "CodeBlock":
                attrs, code = content
                classes = attrs[1]
                if "mermaid" in classes:
                    image = diagram(code)
                    if image.height > 630:
                        scale = 630 / image.height
                        image.scale(scale, scale)
                        image.width *= scale
                        image.height *= scale
                    result += [Spacer(1, 6), image, Spacer(1, 8)]
                    for a, b, label in getattr(image, "_transitions", []):
                        result.append(
                            Paragraph(
                                f"{safe_text(a)} → {safe_text(b)}: {safe_text(label)}",
                                self.style["small"],
                            )
                        )
                else:
                    result.append(CodeBlock(code, next(iter(classes), "text")))
            elif kind == "Div":
                result.extend(self.blocks(content[1], cell))
            elif kind == "BlockQuote":
                result.extend(self.blocks(content, cell))
                result.append(Spacer(1, 5))
            elif kind in {"BulletList", "OrderedList"}:
                items = content if kind == "BulletList" else content[1]
                start = 1 if kind == "BulletList" else content[0][0]
                rendered = [
                    ListItem(flows)
                    for item in items
                    if (flows := self.blocks(item, cell))
                ]
                if rendered:
                    result.append(
                        ListFlowable(
                            rendered,
                            bulletType="bullet" if kind == "BulletList" else "1",
                            start="bullet" if kind == "BulletList" else start,
                            leftIndent=16,
                            bulletFontName="Book",
                            bulletFontSize=8,
                            spaceAfter=7,
                        )
                    )
            elif kind == "Table":
                result.append(self.table(content))
            elif kind == "HorizontalRule":
                result.append(Spacer(1, 12))
            elif kind == "RawBlock":
                if content[0] == "html" and re.fullmatch(
                    r"\s*</?(?:div|span)[^>]*>\s*", content[1]
                ):
                    continue
                if content[1].strip():
                    raise ValueError(
                        f"Unsupported raw block in {self.chapter.source}: "
                        f"{content[1][:120]}"
                    )
            elif kind == "LineBlock":
                result.append(
                    Paragraph(
                        "<br/>".join(self.inline(line) for line in content),
                        self.style["body"],
                    )
                )
            elif kind == "DefinitionList":
                for term, definitions in content:
                    result.append(
                        Paragraph(f"<b>{self.inline(term)}</b>", self.style["body"])
                    )
                    for definition in definitions:
                        result.extend(self.blocks(definition, cell))
            else:
                raise ValueError(f"Unsupported block {kind} in {self.chapter.source}")
        return result

    def table(self, content: list[Any]) -> Table:
        _, _caption, specs, head, bodies, foot = content
        rows = list(head[1])
        for body in bodies:
            rows += body[2] + body[3]
        rows += foot[1]
        data = []
        for _, cells in rows:
            line = []
            for _, _, rowspan, colspan, blocks in cells:
                if rowspan != 1 or colspan != 1:
                    raise ValueError("Spanned table cells need a print adapter")
                line.append(self.blocks(blocks, cell=True))
            data.append(line)
        proportions = [
            spec[1]["c"] if spec[1]["t"] == "ColWidth" else 1 for spec in specs
        ]
        total = sum(proportions)
        table = Table(
            data,
            colWidths=[TEXT_WIDTH * p / total for p in proportions],
            repeatRows=len(head[1]),
            splitInRow=1,
            hAlign="LEFT",
        )
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, len(head[1]) - 1),
                        colors.HexColor("#eeeeF7"),
                    ),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.3, BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        return table


class Book(BaseDocTemplate):
    def __init__(self, destination: Path, **kwargs: Any):
        super().__init__(
            str(destination),
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=55,
            bottomMargin=52,
            title="Python Foundations - FreeCampus",
            author="FreeCampus",
            **kwargs,
        )
        self.running_title = "Python Foundations"
        frame = Frame(
            MARGIN,
            52,
            TEXT_WIDTH,
            HEIGHT - 107,
            id="body",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(
            [
                PageTemplate(id="cover", frames=[frame], onPage=self.cover),
                PageTemplate(id="body", frames=[frame], onPageEnd=self.furniture),
            ]
        )

    def beforeDocument(self) -> None:
        self.running_title = "Python Foundations"

    def afterFlowable(self, flowable: Flowable) -> None:
        if hasattr(flowable, "book_key"):
            self.canv.bookmarkPage(flowable.book_key)
            self.canv.addOutlineEntry(
                flowable.getPlainText(),
                flowable.book_key,
                level=flowable.book_level,
                closed=False,
            )
            self.notify(
                "TOCEntry",
                (
                    flowable.book_level,
                    flowable.getPlainText(),
                    self.page,
                    flowable.book_key,
                ),
            )
            self.running_title = flowable.getPlainText()

    def cover(self, canvas: Any, doc: Any) -> None:
        canvas.setFillColor(PAPER)
        canvas.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
        canvas.setFillColor(VIOLET)
        canvas.rect(0, 0, 14, HEIGHT, fill=1, stroke=0)
        drawing = Drawing(110, 75)
        tree = ET.parse(DOCS / "assets/freecampus-mark.svg")
        for path in tree.getroot():
            if path.tag.endswith("path"):
                drawing.add(
                    SvgPath(
                        path.attrib["d"],
                        fillColor=colors.HexColor("#173f35"),
                        strokeColor=None,
                    )
                )
        drawing.scale(0.36, -0.36)
        renderPDF.draw(drawing, canvas, MARGIN, HEIGHT - 54)
        canvas.setFillColor(INK)
        canvas.setFont("BookBold", 16)
        canvas.drawString(MARGIN + 130, HEIGHT - 88, "FreeCampus")
        canvas.setFont("Book", 10)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN, HEIGHT - 190, "THE COMPLETE STUDY BOOK")
        canvas.setFont("BookBold", 43)
        canvas.setFillColor(INK)
        canvas.drawString(MARGIN, HEIGHT - 260, "Python")
        canvas.drawString(MARGIN, HEIGHT - 315, "Foundations")
        canvas.setFont("Book", 13)
        canvas.setFillColor(MUTED)
        for i, text in enumerate(
            ["From your first program", "to practical, tested Python projects."]
        ):
            canvas.drawString(MARGIN, HEIGHT - 362 - i * 22, text)
        canvas.setStrokeColor(BORDER)
        canvas.line(MARGIN, 190, WIDTH - MARGIN, 190)
        canvas.setFont("BookBold", 11)
        canvas.setFillColor(INK)
        canvas.drawString(MARGIN, 162, "16 units  /  97 lessons  /  16 challenges")
        canvas.setFont("Book", 10)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            MARGIN, 137, "Printable checkpoints, answers, and offline study guidance"
        )
        canvas.drawString(
            MARGIN,
            86,
            f"Curriculum {self.curriculum_version}  •  Free to learn. Open to improve.",
        )
        canvas.linkURL(SITE, (MARGIN, 55, WIDTH - MARGIN, 80), relative=0)
        canvas.drawString(MARGIN, 62, "freecampus.org/python")

    def furniture(self, canvas: Any, doc: Any) -> None:
        canvas.saveState()
        canvas.setFont("Book", 7)
        canvas.setFillColor(MUTED)
        title = self.running_title
        while pdfmetrics.stringWidth(title, "Book", 7) > TEXT_WIDTH - 65:
            title = title[:-2]
        canvas.drawString(MARGIN, HEIGHT - 30, title)
        canvas.setStrokeColor(BORDER)
        canvas.line(MARGIN, HEIGHT - 39, WIDTH - MARGIN, HEIGHT - 39)
        canvas.drawString(MARGIN, 28, "FREECAMPUS  /  PYTHON FOUNDATIONS")
        canvas.drawRightString(WIDTH - MARGIN, 28, str(doc.page))
        canvas.restoreState()


def heading(title: str, key: str, level: int, style: ParagraphStyle) -> Paragraph:
    paragraph = Paragraph(safe_text(title), style)
    paragraph.book_key, paragraph.book_level = key, level
    return paragraph


def build(
    destination: Path, font_directory: Path, limit_units: int | None = None
) -> dict[str, Any]:
    if limit_units is not None and destination.resolve().is_relative_to(
        (DOCS / "_site").resolve()
    ):
        raise ValueError("A partial preview cannot be written to the published site")
    register_fonts(font_directory)
    catalog, course, chapters = course_chapters()
    if limit_units is not None:
        chapters = [c for c in chapters if c.unit < limit_units]
    style = styles()
    answers: list[dict[str, Any]] = []
    story: list[Flowable] = [Spacer(1, 1), NextPageTemplate("body"), PageBreak()]
    for filename in ["about.md", "study-guide.md"]:
        source = ROOT / "scripts/pdf" / filename
        text = source.read_text().replace(
            "{{version}}", str(catalog["curriculum_version"])
        )
        text = text.replace("{{effort}}", course["estimated_effort"])
        intro = Chapter(source, "", 0, "front", filename, text, {})
        ast = markdown_ast(text)
        title = ast.pop(0)
        title_text = "".join(
            t.get("c", " ") for t in title["c"][2] if t["t"] in {"Str", "Space"}
        )
        story.append(heading(title_text, filename, 0, style["title"]))
        story.extend(BookRenderer(intro, style).blocks(ast))
        story.append(PageBreak())
    story.append(heading("Contents", "contents", 0, style["title"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            "tocUnit",
            fontName="BookBold",
            fontSize=10,
            leading=15,
            spaceBefore=9,
            textColor=INK,
        ),
        ParagraphStyle(
            "tocLesson",
            fontName="Book",
            fontSize=8.5,
            leading=12,
            leftIndent=12,
            textColor=MUTED,
        ),
    ]
    story += [toc, PageBreak()]
    for chapter in chapters:
        title = (
            f"Unit {chapter.unit}: {chapter.title.removesuffix(' Overview')}"
            if chapter.kind == "overview"
            else chapter.title
        )
        story.append(
            heading(
                title,
                chapter.key,
                0 if chapter.kind == "overview" else 1,
                style["title"],
            )
        )
        url = SITE + chapter.source.relative_to(DOCS).with_suffix(".html").as_posix()
        story.append(
            Paragraph(
                f'<link href="{url}" color="#5753d9">'
                "Online lesson and runnable notebook</link>",
                style["small"],
            )
        )
        if chapter.metadata.get("description"):
            story.append(
                Paragraph(safe_text(chapter.metadata["description"]), style["body"])
            )
        story.append(Spacer(1, 8))
        print(f"PDF source: {chapter.source.relative_to(ROOT)}", flush=True)
        markdown = prepare_markdown(chapter, answers)
        try:
            story.extend(BookRenderer(chapter, style).blocks(markdown_ast(markdown)))
        except Exception as error:
            raise ValueError(f"Print conversion failed: {chapter.source}") from error
        story.append(PageBreak())
    story.append(heading("Checkpoint answer key", "answer-key", 0, style["title"]))
    story.append(
        Paragraph(
            "Try each checkpoint before reading its answers. Explanations are "
            "included so you can revisit the idea, rather than only check a "
            "letter.",
            style["body"],
        )
    )
    answer_markdown = []
    current = None
    for answer in answers:
        if answer["chapter"] != current:
            current = answer["chapter"]
            answer_markdown.append(f"## {answer['title']}\n")
        quiz = answer["quiz"]
        answer_markdown.append(f"### {quiz['title']}\n")
        for i, q in enumerate(quiz["questions"], 1):
            answer_markdown.append(
                f"**{i}. {chr(65 + q['answer_index'])}.** {q['explanation']}\n"
            )
    story.extend(
        BookRenderer(chapters[0], style).blocks(
            markdown_ast("\n\n".join(answer_markdown))
        )
    )
    story.append(PageBreak())
    story.append(heading("Study record", "study-record", 0, style["title"]))
    story.append(
        Paragraph(
            "Record a date when you can explain the unit's ideas and have "
            "worked through its challenge. This is a personal study record, "
            "not a verified grade or certificate.",
            style["body"],
        )
    )
    data = [["Unit", "Lessons reviewed", "Challenge attempted", "Revisit"]]
    for unit in course["units"]:
        data.append(
            [
                Paragraph(
                    f"{unit['number']}. {safe_text(unit['title'])}", style["cell"]
                ),
                "",
                "",
                "",
            ]
        )
    table = Table(
        data,
        colWidths=[
            TEXT_WIDTH * 0.46,
            TEXT_WIDTH * 0.18,
            TEXT_WIDTH * 0.23,
            TEXT_WIDTH * 0.13,
        ],
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Book"),
                ("FONTSIZE", (0, 0), (-1, 0), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(table)
    story += [PageBreak(), heading("License and source", "license", 0, style["title"])]
    story.append(
        Paragraph(
            'Course sources: <link href="https://github.com/freecampus/python"'
            ' color="#5753d9">github.com/freecampus/python</link>. Report '
            "corrections there or through the website.",
            style["body"],
        )
    )
    license_chapter = Chapter(
        ROOT / "LICENSE", "License", 0, "front", "license", "", {}
    )
    story.extend(
        BookRenderer(license_chapter, style).blocks(
            markdown_ast((ROOT / "LICENSE").read_text())
        )
    )
    story.append(PageBreak())
    story.append(heading("Font licenses", "font-licenses", 0, style["title"]))
    story.append(
        Paragraph(
            "This book embeds DejaVu fonts and renamed glyph subsets from the "
            "Noto family. The Noto subsets retain their original copyright "
            "notices and are distributed under the SIL Open Font License below.",
            style["body"],
        )
    )
    for license_file in sorted((ROOT / "scripts/pdf/fonts").glob("*-license.txt")):
        story.extend(
            BookRenderer(license_chapter, style).blocks(
                markdown_ast(license_file.read_text())
            )
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    book = Book(destination)
    book.curriculum_version = catalog["curriculum_version"]
    book.multiBuild(story)
    from pypdf import PdfReader

    reader = PdfReader(destination)
    manifest = {
        "course_id": course["id"],
        "curriculum_version": catalog["curriculum_version"],
        "source_updated": catalog["last_updated"],
        "units": len({c.unit for c in chapters}),
        "lessons": sum(c.kind == "lesson" for c in chapters),
        "challenges": sum(c.kind == "challenge" for c in chapters),
        "checkpoints": len(answers),
        "questions": sum(len(a["quiz"]["questions"]) for a in answers),
        "pages": len(reader.pages),
        "bytes": destination.stat().st_size,
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "sources": [c.source.relative_to(ROOT).as_posix() for c in chapters],
    }
    destination.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
    subprocess.run(
        [
            "pdftoppm",
            "-f",
            "1",
            "-singlefile",
            "-scale-to",
            "800",
            "-png",
            str(destination),
            str(destination.with_name("python-foundations-cover")),
        ],
        check=True,
    )
    print(json.dumps({k: v for k, v in manifest.items() if k != "sources"}, indent=2))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=DOCS / "_site/downloads/python-foundations.pdf"
    )
    parser.add_argument(
        "--font-directory", type=Path, default=Path("/usr/share/fonts/truetype/dejavu")
    )
    parser.add_argument(
        "--limit-units",
        type=int,
        help="Development preview only; never use for publication",
    )
    args = parser.parse_args()
    build(args.output, args.font_directory, args.limit_units)


if __name__ == "__main__":
    main()
