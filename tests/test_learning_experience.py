import json
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

COURSE_IDS = {
    "python-foundations",
    "intermediate-python",
    "advanced-python",
    "scientific-python",
    "data-science-ml",
}


def _yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def _front_matter(path: Path) -> dict[str, Any]:
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    return yaml.safe_load(text.split("---", 2)[1]) or {}


def _sidebar_paths(contents: list[Any]) -> list[str]:
    paths = []
    for item in contents:
        if isinstance(item, str):
            paths.append(item)
        elif isinstance(item, dict):
            if "href" in item:
                paths.append(item["href"])
            paths.extend(_sidebar_paths(item.get("contents", [])))
    return paths


def _sidebar_section(contents: list[Any], title: str) -> dict[str, Any]:
    for item in contents:
        if not isinstance(item, dict):
            continue
        if item.get("section") == title:
            return item
        try:
            return _sidebar_section(item.get("contents", []), title)
        except LookupError:
            continue
    raise LookupError(title)


def test_quarto_uses_branded_learning_components() -> None:
    quarto = Path("docs/_quarto.yml").read_text()

    assert "brand: _brand.yml" in quarto
    assert "_partials/title-block.html" in quarto
    assert "_includes/course-ui.html" in quarto
    assert "assets/freecampus-mark.svg" in quarto
    assert "components/learning-shell.css" in quarto
    assert "components/landing.css" in quarto
    assert "components/catalog-faq.css" in quarto
    assert "components/course-portfolio.css" in quarto
    assert "components/responsive.css" in quarto


def test_lesson_header_exposes_course_and_progress_identity() -> None:
    title_block = Path("docs/_partials/title-block.html").read_text()
    course_ui = Path("docs/_includes/course-ui.html").read_text()

    assert "$colab_notebook$" in title_block
    assert "$course_id$" in title_block
    assert "$unit_id$" in title_block
    assert "$module_id$" not in title_block
    assert "$lesson_id$" in title_block
    assert "$challenge_id$" in title_block
    assert "$checkpoint_id$" not in title_block
    assert "$project_id$" in title_block
    assert "$completion_label$" in title_block
    assert "data-fc-complete" in title_block
    assert "data-fc-lesson-progress" in title_block
    assert "fcpython.progress.v5" in course_ui
    assert "fcpython.last-lesson.v5" in course_ui
    assert "fcpython.progress.v4" not in course_ui
    assert "legacyProgressKey" not in course_ui
    assert "lessonIdFromKey" in course_ui
    assert "completed_challenges" in course_ui
    assert "capstone_status" in course_ui
    assert "completionSnapshot" in course_ui
    assert "setupChallengeButton" in course_ui
    assert "setupProjectButton" in course_ui
    assert "migrateCourseOwnership" not in course_ui
    assert "migrateLastLessonOwnership" not in course_ui
    assert "isOptionalSidebarLink" not in course_ui
    assert "currentUnit" in course_ui
    assert "currentModule" not in course_ui


def test_course_catalog_is_generated_and_filterable() -> None:
    course_map = Path("docs/courses/index.qmd").read_text()
    template = Path("docs/courses/_listings/course-card.ejs.md").read_text()
    course_ui = Path("docs/_includes/course-ui.html").read_text()

    assert 'contents: "*/index.qmd"' in course_map
    assert "template: _listings/course-card.ejs.md" in course_map
    assert "data-fc-catalog-search" in course_map
    assert "data-fc-course-filter" in course_map
    assert "data-fc-course-card" in template
    assert "data-course-id" in template
    assert "data-course-keywords" in template
    assert "setupCatalog" in course_ui
    assert "Curriculum TBD" in course_ui


def test_course_catalog_has_valid_acyclic_prerequisites() -> None:
    courses = _yaml(Path("docs/courses/_catalog.yml"))["courses"]
    by_id = {course["id"]: course for course in courses}

    assert set(by_id) == COURSE_IDS
    assert len(by_id) == len(courses)
    for course in courses:
        assert set(course["prerequisite_ids"]) <= COURSE_IDS
        assert set(course["recommended_ids"]) <= COURSE_IDS
        assert course["id"] not in course["prerequisite_ids"]

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(course_id: str) -> None:
        assert course_id not in visiting, "course prerequisites must be acyclic"
        if course_id in visited:
            return
        visiting.add(course_id)
        for prerequisite in by_id[course_id]["prerequisite_ids"]:
            visit(prerequisite)
        visiting.remove(course_id)
        visited.add(course_id)

    for course_id in by_id:
        visit(course_id)


def test_course_catalog_owns_every_teaching_lesson_once() -> None:
    catalog = _yaml(Path("docs/courses/_catalog.yml"))
    courses = catalog["courses"]
    owned_paths: set[Path] = set()
    lesson_ids: set[str] = set()

    assert catalog["schema_version"] == 2
    assert catalog["curriculum_version"] == 4
    for course in courses:
        assert "modules" not in course
        course_total = 0
        for unit in course["units"]:
            directory = Path("docs") / unit["directory"]
            metadata = _yaml(directory / "_metadata.yml")
            pages = sorted(
                (
                    page
                    for page in directory.glob("*.qmd")
                    if page.name != "index.qmd" and _front_matter(page).get("lesson_id")
                ),
                key=lambda page: _front_matter(page)["lesson_order"],
            )

            assert metadata["course_id"] == course["id"]
            assert metadata["unit_id"] == unit["id"]
            assert "module_id" not in metadata
            assert len(pages) == unit["lesson_count"]
            assert len({_front_matter(page)["lesson_order"] for page in pages}) == len(
                pages
            )

            for page in pages:
                front_matter = _front_matter(page)
                lesson_id = front_matter["lesson_id"]
                assert lesson_id.startswith(f"{unit['id']}.")
                assert lesson_id not in lesson_ids
                assert page not in owned_paths
                lesson_ids.add(lesson_id)
                owned_paths.add(page)
            course_total += len(pages)

        assert course_total == course["lesson_count"]

    expected = {
        page
        for page in Path("docs/courses").rglob("*.qmd")
        if _front_matter(page).get("lesson_id")
    }
    assert owned_paths == expected
    assert len(lesson_ids) == 53


def test_foundations_unit_reset_uses_only_new_public_routes() -> None:
    assert not Path("docs/lessons").exists()
    foundations_root = Path("docs/courses/python-foundations")
    old_directories = {
        "getting-started",
        "core-python",
        "data-structures",
        "functions",
        "debugging",
        "files-and-data",
        "projects-and-environments",
        "code-quality",
        "object-oriented-python",
        "advanced-python-patterns",
    }
    assert not any(
        (foundations_root / directory).exists() for directory in old_directories
    )
    replaced_unit_directories = {
        "programming-essentials",
        "data-and-reusable-logic",
        "debugging-files-validation",
        "reliable-python-projects",
        "abstraction-and-reusable-patterns",
    }
    assert not any(
        (foundations_root / "units" / directory).exists()
        for directory in replaced_unit_directories
    )

    public_pages = []
    notebook_paths: set[str] = set()
    for page in foundations_root.rglob("*.qmd"):
        front_matter = _front_matter(page)
        notebook = front_matter.get("colab_notebook")
        if not notebook:
            continue
        public_pages.append(page)
        assert "aliases" not in front_matter, page
        assert notebook.startswith("notebooks/courses/python-foundations/"), page
        assert notebook not in notebook_paths, page
        notebook_paths.add(notebook)

    assert len(public_pages) == 79
    assert len(notebook_paths) == 79


def test_course_homes_and_sidebars_match_catalog() -> None:
    courses = _yaml(Path("docs/courses/_catalog.yml"))["courses"]
    quarto = _yaml(Path("docs/_quarto.yml"))
    sidebars = {
        sidebar["title"]: sidebar
        for sidebar in quarto["website"]["sidebar"]
        if sidebar["title"] != "Project Toolkit"
    }

    for course in courses:
        home = Path("docs") / course["home"]
        front_matter = _front_matter(home)
        sidebar = sidebars[course["title"]]
        assert home.exists()
        assert front_matter["course_id"] == course["id"]
        assert front_matter["lesson_count"] == course["lesson_count"]
        assert front_matter["course_status"] == course["status"]
        assert front_matter["estimated_effort"] == course["estimated_effort"]
        assert sidebar["contents"][0] == {
            "href": course["home"],
            "text": "Overview",
        }

        home_text = home.read_text()
        assert "## Before you start" in home_text
        assert "Practice setup:" in home_text
        assert "assessment" in home_text.lower()
        assert "certificate" in home_text.lower()
        if course["lesson_count"]:
            assert "data-fc-course-overview" in home_text
            progress_total = course.get("required_lesson_count", course["lesson_count"])
            assert f'data-course-total="{progress_total}"' in home_text
        else:
            assert course["status"] == "in-development"
            assert "Curriculum TBD" in home_text
            assert "data-fc-course-overview" not in home_text

        sidebar_paths = _sidebar_paths(sidebar["contents"])
        assert sidebar_paths[0] == course["home"]
        assert len(sidebar_paths) == len(set(sidebar_paths))
        expected_paths = {course["home"]}
        previous_unit_position = 0
        challenges_by_unit = {
            challenge["unit_id"]: challenge
            for challenge in course.get("completion", {}).get("required_challenges", [])
        }

        for number, unit in enumerate(course["units"], start=1):
            directory = Path(unit["directory"])
            unit_root = Path("docs") / directory
            unit_home = unit_root / "index.qmd"
            unit_navigation = _sidebar_section(
                sidebar["contents"], f"Unit {number}: {unit['title']}"
            )
            pages = sorted(
                (
                    page
                    for page in unit_root.glob("*.qmd")
                    if page.name != "index.qmd" and _front_matter(page).get("lesson_id")
                ),
                key=lambda page: _front_matter(page)["lesson_order"],
            )
            if unit.get("kind") == "project":
                project_path = course["completion"]["project"]["path"]
                assert unit_navigation["contents"] == [
                    {"href": project_path, "text": "Final project · required"}
                ]
                expected_paths.add(project_path)
                continue

            assert _front_matter(unit_home)["title"] == f"{unit['title']} Overview"
            assert unit_navigation["contents"][0] == {
                "href": (directory / "index.qmd").as_posix(),
                "text": "Overview",
            }
            unit_paths = [(directory / "index.qmd").as_posix()]
            unit_paths.extend(page.relative_to("docs").as_posix() for page in pages)
            if challenge := challenges_by_unit.get(unit["id"]):
                unit_paths.append(challenge["path"])
            unit_position = sidebar_paths.index(unit_paths[0])
            assert unit_position > previous_unit_position
            assert (
                sidebar_paths[unit_position : unit_position + len(unit_paths)]
                == unit_paths
            )
            previous_unit_position = unit_position
            expected_paths.update(unit_paths)
            if challenge := challenges_by_unit.get(unit["id"]):
                assert unit_navigation["contents"][-1] == {
                    "href": challenge["path"],
                    "text": "Unit Challenge · required",
                }
                previous_unit_position = unit_position + len(unit_paths) - 1

        assert set(sidebar_paths) == expected_paths


def test_project_toolkit_starts_with_an_overview() -> None:
    quarto = _yaml(Path("docs/_quarto.yml"))
    sidebar = next(
        item
        for item in quarto["website"]["sidebar"]
        if item["title"] == "Project Toolkit"
    )

    assert sidebar["contents"][0] == {
        "href": "resources/project-toolkit/index.qmd",
        "text": "Overview",
    }
    assert _front_matter(Path("docs/resources/project-toolkit/index.qmd"))["title"] == (
        "Project Toolkit Overview"
    )


def test_foundations_has_versioned_completion_requirements() -> None:
    courses = _yaml(Path("docs/courses/_catalog.yml"))["courses"]
    foundations = next(
        course for course in courses if course["id"] == "python-foundations"
    )
    completion = foundations["completion"]
    required = set(completion["required_lesson_ids"])
    optional = set(completion["optional_lesson_ids"])

    assert completion["curriculum_version"] == 4
    assert completion["rule_version"] == 4
    assert completion["recognition"] == "local-self-reported"
    assert len(required) == foundations["required_lesson_count"] == 38
    assert not optional
    assert foundations["optional_lesson_count"] == 0

    metadata_by_id = {}
    for unit in foundations["units"]:
        directory = Path("docs") / unit["directory"]
        for page in directory.glob("*.qmd"):
            front_matter = _front_matter(page)
            if lesson_id := front_matter.get("lesson_id"):
                metadata_by_id[lesson_id] = front_matter

    assert set(metadata_by_id) == required
    for lesson_id in required:
        assert "required_for_completion" not in metadata_by_id[lesson_id]
        assert "completion_label" not in metadata_by_id[lesson_id]

    instructional_units = {
        unit["id"] for unit in foundations["units"] if unit["kind"] == "instructional"
    }
    challenges = completion["required_challenges"]
    assert len(challenges) == len(instructional_units) == 20
    assert {challenge["unit_id"] for challenge in challenges} == instructional_units
    assert {challenge["id"] for challenge in challenges} == {
        f"{unit_id}.challenge" for unit_id in instructional_units
    }
    assert not Path("docs/courses/python-foundations/milestones").exists()
    for challenge in challenges:
        challenge_path = Path("docs") / challenge["path"]
        front_matter = _front_matter(challenge_path)
        assert challenge_path.exists()
        assert challenge["required"] is True
        assert front_matter["challenge_id"] == challenge["id"]
        assert front_matter["assessment_type"] == "unit-challenge"
        assert front_matter["required_for_completion"] is True

    project = completion["project"]
    project_path = Path("docs") / project["path"]
    project_front_matter = _front_matter(project_path)
    project_text = project_path.read_text()
    assert project_front_matter["project_id"] == project["id"]
    assert project_front_matter["rubric_version"] == project["rubric_version"] == 2
    assert project_front_matter["required_for_completion"] is True
    assert "| Criterion | Not yet | Meets the requirement |" in project_text
    assert "not a submission" in project_text.lower()


def test_foundations_unit_challenges_are_guided_and_self_checking() -> None:
    challenge_pages = sorted(
        Path("docs/courses/python-foundations/units").glob("*/challenge.qmd")
    )

    assert len(challenge_pages) == 20
    for path in challenge_pages:
        front_matter = _front_matter(path)
        text = path.read_text()
        unit_id = path.parent.name

        assert front_matter["challenge_id"] == f"{unit_id}.challenge"
        assert front_matter["required_for_completion"] is True
        assert front_matter["assessment_type"] == "unit-challenge"
        assert front_matter["colab_notebook"].endswith(
            f"/units/{unit_id}/challenge.ipynb"
        )
        assert "data-fc-challenge-complete" in text
        assert "ojs-quiz.qmd" in text
        assert "colab-link.qmd" in text

        if unit_id == "getting-started":
            assert front_matter["challenge_format"] == "quiz"
            assert "<!-- fcpython-unit-challenge: quiz -->" in text
            assert "8 of 10" in text
            continue

        assert front_matter["challenge_format"] == "guided-programming"
        assert front_matter["estimated_time"] == "60\N{EN DASH}120 minutes"
        assert "<!-- fcpython-unit-challenge: practical -->" in text
        assert "## 3. Start from the contract" in text
        assert "## 5. Run progressive assertions" in text
        assert "## 6. Use the hint ladder only when needed" in text
        assert "## 7. Keep debugging evidence" in text
        assert text.count("<summary>Hint ") == 3
        assert "```python" in text
        assert "assert " in text


def test_software_courses_use_problem_complexity_as_the_level_boundary() -> None:
    courses = _yaml(Path("docs/courses/_catalog.yml"))["courses"]
    by_id = {course["id"]: course for course in courses}
    foundations = by_id["python-foundations"]
    intermediate = by_id["intermediate-python"]
    advanced = by_id["advanced-python"]

    assert foundations["lesson_count"] == 38
    assert [unit["id"] for unit in foundations["units"]] == [
        "getting-started",
        "values-types-input-output",
        "control-flow",
        "data-structures",
        "functions",
        "debugging",
        "files",
        "error-handling-and-validation",
        "modules-and-packages",
        "project-structure",
        "environments-and-dependencies",
        "command-line-programs",
        "testing",
        "code-style-and-linting",
        "typing",
        "automation-and-ci",
        "object-oriented-programming",
        "comprehensions-and-iteration",
        "decorators-and-context-managers",
        "logging-and-configuration",
        "foundations-project",
    ]
    assert intermediate["title"] == "Intermediate Python: Applied Problem Solving"
    assert advanced["title"] == "Advanced Python: Complex Problem Solving"
    for course in (intermediate, advanced):
        assert course["status"] == "in-development"
        assert course["lesson_count"] == 0
        assert course["units"] == []
        assert course["estimated_effort"] == "TBD"

    intermediate_home = Path("docs/courses/intermediate-python/index.qmd").read_text()
    advanced_home = Path("docs/courses/advanced-python/index.qmd").read_text()
    assert "progressively harder problems" in intermediate_home
    assert "Planned challenge format" in intermediate_home
    assert re.search(r"complex problems under\s+real\s+constraints", advanced_home)
    assert "Planned challenge format" in advanced_home


def test_progress_v5_tracks_unit_challenges_without_legacy_migration() -> None:
    old_storage = {
        "fcpython.progress.v4": json.dumps(
            {
                "schema_version": 4,
                "courses": {
                    "python-foundations": {
                        "completed_checkpoints": {"core-programming": "old-record"}
                    }
                },
            }
        )
    }
    course_ui = Path("docs/_includes/course-ui.html").read_text()
    script = course_ui.split("<script>", 1)[1].rsplit("</script>", 1)[0]
    script = (
        script.rsplit("})();", 1)[0]
        + """
window.__fcTest = {
  currentKey,
  lessonId,
  progress,
  unitChallengeId: challengeIdFromKey(
    "courses/python-foundations/units/values-types-input-output/challenge"
  ),
  challengeIsLesson: isLessonKey(
    "courses/python-foundations/units/values-types-input-output/challenge"
  ),
};
})();
"""
    )
    lesson_url = (
        "https://freecampus.github.io/python/courses/python-foundations/units/"
        "values-types-input-output/values-variables-types.html"
    )
    lesson_path = (
        "/python/courses/python-foundations/units/values-types-input-output/"
        "values-variables-types.html"
    )
    harness = f"""
const storage = new Map(Object.entries({json.dumps(old_storage)}));
global.window = {{
  location: {{
    href: {json.dumps(lesson_url)},
    pathname: {json.dumps(lesson_path)},
  }},
  localStorage: {{
    getItem: (key) => storage.has(key) ? storage.get(key) : null,
    setItem: (key, value) => storage.set(key, value),
  }},
}};
global.document = {{
  querySelector: () => null,
  querySelectorAll: () => [],
  body: {{ classList: {{ add: () => {{}} }} }},
  title: "Values, Variables, and Types",
}};
{script}
process.stdout.write(JSON.stringify({{
  state: window.__fcTest,
  oldProgress: JSON.parse(storage.get("fcpython.progress.v4")),
  newProgress: storage.get("fcpython.progress.v5") || null,
}}));
"""
    result = subprocess.run(
        ["node"], input=harness, text=True, capture_output=True, check=True
    )
    observed = json.loads(result.stdout)

    assert observed["state"]["currentKey"] == (
        "courses/python-foundations/units/values-types-input-output/values-variables-types"
    )
    assert observed["state"]["lessonId"] == (
        "values-types-input-output.values-variables-types"
    )
    assert observed["state"]["unitChallengeId"] == (
        "values-types-input-output.challenge"
    )
    assert observed["state"]["challengeIsLesson"] is False
    assert observed["state"]["progress"] == {"schema_version": 5, "courses": {}}
    assert observed["oldProgress"]["schema_version"] == 4
    assert observed["newProgress"] is None


def test_navbar_links_every_course() -> None:
    quarto = _yaml(Path("docs/_quarto.yml"))
    courses = _yaml(Path("docs/courses/_catalog.yml"))["courses"]
    navbar_items = quarto["website"]["navbar"]["left"]
    courses_menu = next(item for item in navbar_items if item.get("text") == "Courses")
    menu_hrefs = {item["href"] for item in courses_menu["menu"] if "href" in item}

    assert "courses/index.qmd" in menu_hrefs
    assert {course["home"] for course in courses} <= menu_hrefs
    assert any(item.get("href") == "pathways/index.qmd" for item in navbar_items)


def test_homepage_demo_is_preserved_as_raw_html() -> None:
    home = Path("docs/index.qmd").read_text()
    raw_blocks = re.findall(r"```{=html}\n(.*?)\n```", home, flags=re.DOTALL)
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
    faq_index = Path("docs/resources/faq/index.qmd").read_text()
    faq_metadata = Path("docs/resources/faq/_metadata.yml").read_text()

    assert faq_index.index("## Find your question") < faq_index.index(
        "## How to use this FAQ"
    )
    assert "data-fc-faq-search" in faq_index
    assert "sidebar: false" in faq_metadata
