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
            raise ValueError(f"Missing course activity: {source}")
    print(
        f"Verified complete Foundations book: {manifest['pages']} pages, "
        f"{manifest['lessons']} lessons, {manifest['questions']} printable questions."
    )


if __name__ == "__main__":
    verify()
