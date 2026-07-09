from __future__ import annotations

import html
import json
import re
from pathlib import Path

import pytest

from fcpython.questions import MultipleChoiceQuestion, Quiz
from fcpython.quiz_banks import values_variables_types_quiz
from fcpython.widgets import quiz_summary, show_quiz


def test_multiple_choice_question_validates_answer_index() -> None:
    with pytest.raises(ValueError, match="answer_index"):
        MultipleChoiceQuestion(
            id="bad",
            prompt="Bad question?",
            options=("A", "B"),
            answer_index=2,
            explanation="The answer index is outside the options.",
        )


def test_quiz_rejects_duplicate_question_ids() -> None:
    question = MultipleChoiceQuestion(
        id="same",
        prompt="Question?",
        options=("A", "B"),
        answer_index=0,
        explanation="A is correct.",
    )

    with pytest.raises(ValueError, match="unique"):
        Quiz(id="quiz", title="Quiz", questions=(question, question))


def test_values_variables_types_quiz_serializes_to_json() -> None:
    quiz = values_variables_types_quiz()
    payload = json.loads(quiz.to_json())

    assert payload["id"] == "values-variables-types"
    assert len(payload["questions"]) == 4
    assert payload["questions"][0]["answer_index"] == 2


def test_quiz_json_script_contains_application_json_tag() -> None:
    script = values_variables_types_quiz().to_json_script()

    assert 'type="application/json"' in script
    assert 'class="fcpython-ojs-quiz-config"' in script
    assert "Values, variables, and types checkpoint" in script


def test_quiz_summary_returns_prompts() -> None:
    prompts = quiz_summary(values_variables_types_quiz())

    assert len(prompts) == 4
    assert prompts[0].startswith("What is the type")


def test_show_quiz_returns_widget_container() -> None:
    widget = show_quiz(values_variables_types_quiz())

    assert widget.__class__.__name__ == "VBox"
    assert len(widget.children) > 1


def test_lesson_ojs_quiz_config_matches_quiz_bank() -> None:
    lesson = Path("docs/lessons/core-python/values-variables-types.qmd").read_text()
    match = re.search(
        r'<script type="application/json" class="fcpython-ojs-quiz-config">'
        r"\n(.*?)\n"
        r"</script>",
        lesson,
        flags=re.DOTALL,
    )

    assert match is not None
    lesson_payload = json.loads(html.unescape(match.group(1)))
    assert lesson_payload == values_variables_types_quiz().to_dict()


def _lesson_pages() -> list[Path]:
    return sorted(
        path
        for path in Path("docs/lessons").rglob("*.qmd")
        if "_includes" not in path.parts and path.name != "_lesson-template.qmd"
    )


def _content_lesson_pages() -> list[Path]:
    skipped = {"index.qmd", "learner-profiles.qmd", "instructor-notes.qmd"}
    return [path for path in _lesson_pages() if path.name not in skipped]


def test_all_lessons_include_ojs_quiz() -> None:
    missing = []
    for path in _lesson_pages():
        text = path.read_text()
        has_config = 'class="fcpython-ojs-quiz-config"' in text
        has_ojs_include = "ojs-quiz.qmd" in text
        if not has_config or not has_ojs_include:
            missing.append(str(path))

    assert missing == []


def test_all_lesson_quiz_payloads_are_valid_json() -> None:
    payloads = []
    for path in _lesson_pages():
        text = path.read_text()
        matches = re.findall(
            r'<script type="application/json" class="fcpython-ojs-quiz-config">'
            r"\n(.*?)\n"
            r"</script>",
            text,
            flags=re.DOTALL,
        )
        payloads.extend((path, match) for match in matches)

    assert payloads
    for path, payload in payloads:
        parsed = json.loads(html.unescape(payload))
        assert parsed["id"], path
        assert parsed["questions"], path


def test_lessons_do_not_use_generic_generated_scaffold() -> None:
    forbidden_phrases = tuple(
        phrase.casefold()
        for phrase in (
            "Mental model",
            "mental model",
            "Tiny example",
            "tiny example",
            "Walkthrough",
            "read this line slowly",
            "building one mental model",
            "Visual model",
            "visual model",
            "visual-model",
            "mermaid-visual-model",
        )
    )
    hits = []
    for path in _lesson_pages():
        text = path.read_text().casefold()
        for phrase in forbidden_phrases:
            if phrase in text:
                hits.append(f"{path}: {phrase}")

    assert hits == []


def test_course_links_match_repository_remote() -> None:
    quarto = Path("docs/_quarto.yml").read_text()
    pyproject = Path("pyproject.toml").read_text()

    assert "https://github.com/freecampus/python" in quarto
    assert "https://freecampus.github.io/python/" in quarto
    assert "https://github.com/freecampus/python" in pyproject
    assert "freecampus-org/python" not in quarto
    assert "freecampus-org/python" not in pyproject


def test_content_lessons_include_orientation_metadata() -> None:
    missing = []
    for path in _content_lesson_pages():
        text = path.read_text()
        if "::: {.lesson-meta}" not in text:
            missing.append(str(path))

    assert missing == []


def test_lesson_front_matter_supports_future_listings() -> None:
    missing = []
    for path in _lesson_pages():
        text = path.read_text()
        front_matter = text.split("---", 2)[1] if text.startswith("---") else ""
        if "categories:" not in front_matter or "order:" not in front_matter:
            missing.append(str(path))

    assert missing == []


def test_lessons_use_quarto_callouts_for_standard_boxes() -> None:
    old_box_classes = (
        "{.learning-objectives}",
        "{.questions}",
        "{.key-idea}",
        "{.analogy}",
        "{.challenge}",
        "{.practice-box}",
        "{.debugging-corner}",
        "{.lesson-summary}",
        "{.key-points}",
        "{.instructor-note}",
        "{.setup-check}",
        "{.responsible-ai}",
        "{.toolbox}",
        "{.project-box}",
    )
    hits = []
    for path in _lesson_pages():
        text = path.read_text()
        for old_class in old_box_classes:
            if old_class in text:
                hits.append(f"{path}: {old_class}")

    assert hits == []


def test_lessons_use_clean_numbered_section_headings() -> None:
    old_section_patterns = (
        re.compile(r"^#{2,4} Section \d+:", flags=re.MULTILINE),
        re.compile(r"^- Section \d+:", flags=re.MULTILINE),
        re.compile(r"^#{2,4} Section checkpoint$", flags=re.MULTILINE),
    )
    hits = []
    for path in _lesson_pages():
        text = path.read_text()
        for pattern in old_section_patterns:
            if pattern.search(text):
                hits.append(f"{path}: {pattern.pattern}")

    assert hits == []


def test_selected_lessons_include_mermaid_diagrams() -> None:
    expected = {
        Path("docs/lessons/core-python/values-variables-types.qmd"),
        Path("docs/lessons/core-python/booleans-and-conditionals.qmd"),
        Path("docs/lessons/core-python/loops-and-tracing.qmd"),
        Path("docs/lessons/functions/function-basics.qmd"),
        Path("docs/lessons/data-structures/lists.qmd"),
        Path("docs/lessons/data-structures/dictionaries.qmd"),
        Path("docs/lessons/data-structures/nested-data.qmd"),
        Path("docs/lessons/debugging/error-messages.qmd"),
        Path(
            "docs/lessons/projects-and-environments/environments-and-dependencies.qmd"
        ),
        Path("docs/lessons/machine-learning-ai/training-and-evaluation.qmd"),
    }

    missing = [
        str(path) for path in sorted(expected) if "```{mermaid}" not in path.read_text()
    ]

    assert missing == []


def test_mermaid_blocks_are_not_empty() -> None:
    blocks = []
    for path in _lesson_pages():
        text = path.read_text()
        blocks.extend(
            (path, block)
            for block in re.findall(
                r"```\{mermaid\}\n(.*?)\n```", text, flags=re.DOTALL
            )
        )

    assert len(blocks) >= 10
    for path, block in blocks:
        assert block.strip(), path


def test_mermaid_blocks_are_rendered_not_echoed_as_code() -> None:
    missing_options = []
    for path in _lesson_pages():
        text = path.read_text()
        for block in re.findall(r"```\{mermaid\}\n(.*?)\n```", text, flags=re.DOTALL):
            lines = block.splitlines()
            if lines[:2] != ["%%| echo: false", "%%| eval: true"]:
                missing_options.append(str(path))

    assert missing_options == []
