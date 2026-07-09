from __future__ import annotations

import html
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType

import pytest

from fcpython.questions import MultipleChoiceQuestion, Quiz
from fcpython.quiz_banks import values_variables_types_quiz
from fcpython.widgets import quiz_summary, show_quiz


def _load_notebook_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "build_colab_notebooks", Path("scripts/build_colab_notebooks.py")
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


notebook_builder = _load_notebook_builder()


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


def _front_matter(path: Path) -> str:
    text = path.read_text()
    return text.split("---", 2)[1] if text.startswith("---") else ""


def test_all_lessons_include_ojs_quiz() -> None:
    missing = []
    for path in _lesson_pages():
        text = path.read_text()
        has_config = 'class="fcpython-ojs-quiz-config"' in text
        has_ojs_include = "ojs-quiz.qmd" in text
        if not has_config or not has_ojs_include:
            missing.append(str(path))

    assert missing == []


def test_all_lessons_include_colab_launch_link() -> None:
    include = Path("docs/lessons/_includes/colab-link.qmd").read_text()
    assert "colab.research.google.com/github/freecampus/python/blob/gh-pages" in include
    assert "{{< meta colab_notebook >}}" in include

    missing = []
    for path in _lesson_pages():
        text = path.read_text()
        front_matter = _front_matter(path)
        if "colab-link.qmd" not in text or "colab_notebook:" not in front_matter:
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
            "fcpython-masterclass",
            "guided master-class",
            "Practice in Colab",
            "Practice in Google Colab",
            "identify the value, name, or action on this line",
            "a word you should be able to explain after this lesson",
        )
    )
    hits = []
    for path in _lesson_pages():
        text = path.read_text().casefold()
        for phrase in forbidden_phrases:
            if phrase in text:
                hits.append(f"{path}: {phrase}")

    assert hits == []


def test_content_lessons_are_hands_on_episodes() -> None:
    missing = []
    for path in _content_lesson_pages():
        text = path.read_text()
        required = (
            "<!-- fcpython-lab: start -->",
            "## Questions",
            "## Objectives",
            "## Hands-on episode:",
            "```",
            '::: {.callout-note title="Challenge"}',
            "## Key points",
        )
        if any(marker not in text for marker in required):
            missing.append(str(path))

    assert missing == []


def test_chapter_and_support_pages_explain_hands_on_use() -> None:
    missing = []
    for path in _lesson_pages():
        if path.name not in {
            "index.qmd",
            "learner-profiles.qmd",
            "instructor-notes.qmd",
        }:
            continue
        text = path.read_text()
        if "<!-- fcpython-chapter-lab: start -->" not in text:
            missing.append(str(path))

    assert missing == []


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
        front_matter = _front_matter(path)
        required = ("categories:", "order:", "colab_notebook:")
        if any(field not in front_matter for field in required):
            missing.append(str(path))

    assert missing == []


def test_colab_notebook_paths_match_lesson_paths() -> None:
    mismatches = []
    for path in _lesson_pages():
        expected = notebook_builder.notebook_path_for(path).as_posix()
        if f'colab_notebook: "{expected}"' not in _front_matter(path):
            mismatches.append(str(path))

    assert mismatches == []


def test_qmd_to_notebook_turns_python_fences_into_code_cells() -> None:
    path = Path("docs/lessons/core-python/values-variables-types.qmd")
    notebook = notebook_builder.qmd_to_notebook(path)
    code_sources = [
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    ]

    assert any("price = 12.50" in source for source in code_sources)
    assert all("fcpython-ojs-quiz-config" not in source for source in code_sources)


def test_build_colab_notebooks_writes_expected_files(tmp_path: Path) -> None:
    written = notebook_builder.build_notebooks(output_root=tmp_path)
    expected = tmp_path / "core-python/values-variables-types.ipynb"

    assert expected in written
    payload = json.loads(expected.read_text())
    assert payload["nbformat"] == 4
    assert any(cell["cell_type"] == "code" for cell in payload["cells"])


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
