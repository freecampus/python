import re
import subprocess
from pathlib import Path


def test_quarto_uses_branded_learning_components() -> None:
    quarto = Path("docs/_quarto.yml").read_text()

    assert "brand: _brand.yml" in quarto
    assert "_partials/title-block.html" in quarto
    assert "_includes/course-ui.html" in quarto
    assert "assets/freecampus-mark.svg" in quarto
    assert "components/learning-shell.css" in quarto
    assert "components/landing.css" in quarto
    assert "components/catalog-faq.css" in quarto
    assert "components/responsive.css" in quarto


def test_lesson_header_exposes_colab_and_progress_actions() -> None:
    title_block = Path("docs/_partials/title-block.html").read_text()
    course_ui = Path("docs/_includes/course-ui.html").read_text()

    assert "$colab_notebook$" in title_block
    assert "data-fc-complete" in title_block
    assert "data-fc-lesson-progress" in title_block
    assert "fcpython.progress.v1" in course_ui
    assert "fcpython.last-lesson.v1" in course_ui


def test_course_catalog_is_generated_and_filterable() -> None:
    course_map = Path("docs/lessons/index.qmd").read_text()
    template = Path("docs/lessons/_listings/course-card.ejs.md").read_text()
    course_ui = Path("docs/_includes/course-ui.html").read_text()

    assert 'contents: "*/index.qmd"' in course_map
    assert "template: _listings/course-card.ejs.md" in course_map
    assert "data-fc-catalog-search" in course_map
    assert "data-fc-stage" in course_map
    assert "data-course-path" in template
    assert "chapterSection?.textContent" in course_ui
    assert "catalogSupplementalTerms" in course_ui


def test_homepage_demo_is_preserved_as_raw_html() -> None:
    home = Path("docs/index.qmd").read_text()
    raw_blocks = re.findall(r"```\{=html\}\n(.*?)\n```", home, flags=re.DOTALL)
    demo = next(block for block in raw_blocks if 'class="fc-demo-window"' in block)

    rendered = subprocess.run(
        ["quarto", "pandoc", "--from", "markdown", "--to", "html"],
        input=f"```{{=html}}\n{demo}\n```\n",
        text=True,
        capture_output=True,
        check=True,
    ).stdout

    assert '<span class="fc-demo-dots"' in rendered
    assert '<div class="fc-demo-output">' in rendered
    assert '<div class="fc-demo-loop"' in rendered
    assert "&lt;span" not in rendered


def test_lesson_metadata_remains_visible() -> None:
    learning_shell = Path("docs/components/learning-shell.css").read_text()
    hidden_rules = re.findall(
        r"([^{}]+)\{\s*display:\s*none;\s*\}", learning_shell, flags=re.DOTALL
    )

    assert all(".lesson-meta" not in selectors for selectors in hidden_rules)


def test_faq_is_search_first_and_sidebar_free() -> None:
    faq_index = Path("docs/lessons/faq/index.qmd").read_text()
    faq_metadata = Path("docs/lessons/faq/_metadata.yml").read_text()

    assert faq_index.index("## Find your question") < faq_index.index(
        "## How to use this FAQ"
    )
    assert "data-fc-faq-search" in faq_index
    assert "sidebar: false" in faq_metadata
