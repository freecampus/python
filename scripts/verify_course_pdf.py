"""Fail publishing if the Foundations download is incomplete or inconsistent."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def verify() -> None:
    downloads = ROOT / "docs/_site/downloads"
    pdf = downloads / "python-foundations.pdf"
    cover = downloads / "python-foundations-cover.png"
    manifest = json.loads(pdf.with_suffix(".json").read_text())
    catalog = yaml.safe_load((ROOT / "docs/courses/_catalog.yml").read_text())
    course = next(c for c in catalog["courses"] if c["id"] == "python-foundations")
    expected = {
        "course_id": course["id"],
        "curriculum_version": catalog["curriculum_version"],
        "units": len(course["units"]),
        "lessons": course["lesson_count"],
        "challenges": len(course["completion"]["challenges"]),
        "bytes": pdf.stat().st_size,
        "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
    }
    for key, value in expected.items():
        if manifest[key] != value:
            raise ValueError(f"PDF manifest mismatch: {key}")
    reader = PdfReader(pdf)
    if len(reader.pages) != manifest["pages"] or not reader.outline:
        raise ValueError("Missing pages or navigable PDF outline")
    if not cover.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Missing PNG cover preview")
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    for marker in [
        "About this edition",
        "How to study with this book",
        "Checkpoint answer key",
        "Study record",
        "BSD 3-Clause License",
    ]:
        if marker not in text:
            raise ValueError(f"Missing PDF section: {marker}")
    for source in manifest["sources"]:
        metadata = yaml.safe_load((ROOT / source).read_text().split("---", 2)[1])
        if metadata["title"] not in text and not source.endswith("/index.qmd"):
            raise Value…4254 tokens truncated…horing templates
├── notebooks/
├── src/fcpython/
└── tests/
```

### Downloadable Foundations book

The documentation publishing job builds a complete A4 study book from the
canonical Foundations QMD files. The Python home page and Foundations overview
link to `downloads/python-foundations.pdf`. The cover PNG and JSON manifest are
generated alongside it; the manifest supplies the displayed page count, file
size, and curriculum version. PDF binaries are build artifacts, not tracked
sources.

Install `scripts/pdf/requirements.txt`, Quarto, `fonts-dejavu-core`, and
`poppler-utils`, then run:

```bash
makim docs.build     # Website, Colab notebooks, and the complete PDF
makim docs.site      # Website and notebooks only, for faster local iteration
makim docs.pdf       # PDF, cover preview, and manifest only
python scripts/verify_course_pdf.py
```

The PDF includes all unit overviews, lessons, and challenges in catalog order.
Its separate front matter explains offline study and printed code wrapping.
Browser quizzes become printable questions with an answer key; hints and
solutions are visible, diagrams become page-sized vectors, and lesson links
return to the website and Colab. No lesson code executes during the build.
PDF reading does not update browser progress or create a verified credential.

For a quick development preview, use `--limit-units 1 --output build/pdf/preview.pdf`
with `scripts/build_course_pdf.py`. Never publish a preview as the complete book.
The documentation workflow verifies the complete artifact before publishing and
uploads the book, cover, and manifest for pull-request review.
