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
    assert "$completion_label$" not in title_block
    assert "data-fc-complete" in title_block
    assert "data-fc-lesson-progress" in title_block
    assert "fcpython.progress.v6" in course_ui
    assert "fcpython.last-lesson.v6" in course_ui
    assert "fcpython.progress.v5" not in course_ui
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
    assert catalog["curriculum_version"] == 19
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
            if course["id"] == "python-foundations":
                assert unit["number"] >= 0
                assert metadata["unit_number"] == unit["number"]
            assert len(pages) == unit["lesson_count"]
            assert len({_front_matter(page)["lesson_order"] for page in pages}) == len(
                pages
            )

            for page in pages:
                front_matter = _front_matter(page)
                lesson_id = front_matter["lesson_id"]
                assert lesson_id.startswith(f"{unit['id']}.")
                if course["id"] == "python-foundations":
                    assert front_matter["unit_id"] == unit["id"]
                    assert front_matter["unit_number"] == unit["number"]
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
    assert len(lesson_ids) == 108


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
        "learning-workflow-tools",
        "numeric-foundations",
        "text-input-output",
        "decisions",
        "loops-and-state",
        "sequences",
        "mappings-and-sets",
        "mutability-and-copying",
        "functions-and-interfaces",
        "scope-and-call-stacks",
        "debugging",
        "files-and-paths",
        "structured-data-and-patterns",
        "exceptions-and-validation",
        "modules-and-standard-library",
        "reproducible-projects",
        "git-and-collaboration",
        "testing-with-pytest",
        "maintainable-code",
        "pythonic-iteration",
        "reliable-project-operations",
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

    assert len(public_pages) == 125
    assert len(notebook_paths) == 125


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
            assert f'data-course-total="{course["lesson_count"]}"' in home_text
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
            for challenge in course.get("completion", {}).get("challenges", [])
        }

        for unit in course["units"]:
            number = unit.get("number")
            if number is None:
                number = course["units"].index(unit) + 1
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
                    "text": "Unit Challenge",
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


def test_foundations_has_versioned_course_sequence() -> None:
    courses = _yaml(Path("docs/courses/_catalog.yml"))["courses"]
    foundations = next(
        course for course in courses if course["id"] == "python-foundations"
    )
    completion = foundations["completion"]
    lesson_ids = set(completion["lesson_ids"])
    home_path = Path("docs/courses/python-foundations/index.qmd")
    home_metadata = _front_matter(home_path)
    home_text = home_path.read_text()
    course_ui = Path("docs/_includes/course-ui.html").read_text()
    progress_ids_match = re.search(r'data-course-lesson-ids="([^"]+)"', home_text)

    assert completion["curriculum_version"] == 19
    assert completion["rule_version"] == 10
    assert completion["recognition"] == "local-self-reported"
    assert len(lesson_ids) == foundations["lesson_count"] == 93
    assert home_metadata["lesson_ids"] == completion["lesson_ids"]
    assert progress_ids_match is not None
    assert progress_ids_match.group(1).split() == completion["lesson_ids"]
    assert f"curriculum version {completion['curriculum_version']}" in home_text
    assert "curriculum_version: 19" in course_ui
    assert "state.curriculum_version = 19" in course_ui
    assert "completion_rule_version: 10" in course_ui
    assert "state.completion_rule_version = 10" in course_ui
    assert "required_lesson_count" not in foundations
    assert "optional_lesson_count" not in foundations

    metadata_by_id = {}
    for unit in foundations["units"]:
        directory = Path("docs") / unit["directory"]
        for page in directory.glob("*.qmd"):
            front_matter = _front_matter(page)
            if lesson_id := front_matter.get("lesson_id"):
                metadata_by_id[lesson_id] = front_matter

    assert set(metadata_by_id) == lesson_ids
    for lesson_id in lesson_ids:
        assert "required_for_completion" not in metadata_by_id[lesson_id]
        assert "completion_label" not in metadata_by_id[lesson_id]

    instructional_units = {
        unit["id"] for unit in foundations["units"] if unit["kind"] == "instructional"
    }
    challenges = completion["challenges"]
    assert len(challenges) == len(instructional_units) == 16
    assert {challenge["unit_id"] for challenge in challenges} == instructional_units
    assert {challenge["id"] for challenge in challenges} == {
        f"{unit_id}.challenge" for unit_id in instructional_units
    }
    assert not Path("docs/courses/python-foundations/milestones").exists()
    for challenge in challenges:
        challenge_path = Path("docs") / challenge["path"]
        front_matter = _front_matter(challenge_path)
        assert challenge_path.exists()
        assert "required" not in challenge
        assert front_matter["challenge_id"] == challenge["id"]
        assert front_matter["assessment_type"] == "unit-challenge"
        assert "required_for_completion" not in front_matter
        assert "completion_label" not in front_matter

    assert "project" not in completion
    assert not Path("docs/courses/python-foundations/project").exists()


def test_foundations_outcome_map_covers_the_course_once() -> None:
    outcomes = _yaml(Path("docs/courses/python-foundations/_outcomes.yml"))
    foundations = next(
        course
        for course in _yaml(Path("docs/courses/_catalog.yml"))["courses"]
        if course["id"] == "python-foundations"
    )
    mapped_units = outcomes["units"]

    assert outcomes["schema_version"] == 1
    assert (
        outcomes["curriculum_version"]
        == foundations["completion"]["curriculum_version"]
    )
    assert [unit["id"] for unit in mapped_units] == [
        unit["id"] for unit in foundations["units"]
    ]
    assert {lesson for unit in mapped_units for lesson in unit["lesson_ids"]} == set(
        foundations["completion"]["lesson_ids"]
    )
    assert {unit["challenge_id"] for unit in mapped_units} == {
        challenge["id"] for challenge in foundations["completion"]["challenges"]
    }
    graduate_ids = set(outcomes["graduate_outcomes"])
    assert graduate_ids
    assert all(
        set(unit["graduate_outcome_ids"]) <= graduate_ids for unit in mapped_units
    )


def test_foundations_unit_challenges_are_guided_and_self_checking() -> None:
    challenge_pages = sorted(
        Path("docs/courses/python-foundations/units").glob("*/challenge.qmd")
    )

    assert len(challenge_pages) == 16
    for path in challenge_pages:
        front_matter = _front_matter(path)
        text = path.read_text()
        unit_id = path.parent.name

        assert front_matter["challenge_id"] == f"{unit_id}.challenge"
        assert "required_for_completion" not in front_matter
        assert "completion_label" not in front_matter
        assert front_matter["assessment_type"] == "unit-challenge"
        assert front_matter["colab_notebook"].endswith(
            f"/units/{unit_id}/challenge.ipynb"
        )
        assert "data-fc-challenge-complete" in text
        assert "ojs-quiz.qmd" in text
        assert "colab-link.qmd" in text

        if unit_id == "get-started":
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
        assert "```python" in text or "```bash" in text
        assert "assert " in text or "Evidence targets:" in text


def test_software_courses_use_problem_complexity_as_the_level_boundary() -> None:
    courses = _yaml(Path("docs/courses/_catalog.yml"))["courses"]
    by_id = {course["id"]: course for course in courses}
    foundations = by_id["python-foundations"]
    intermediate = by_id["intermediate-python"]
    advanced = by_id["advanced-python"]

    assert foundations["lesson_count"] == 93
    assert [unit["id"] for unit in foundations["units"]] == [
        "get-started",
        "python-syntax",
        "core-values-types",
        "collections-iteration",
        "decisions-repetition",
        "functions-call-behavior",
        "mutability-identity-copying",
        "problem-solving-algorithms",
        "errors-exceptions-debugging",
        "files-paths-external-data",
        "modules-environments-projects",
        "object-oriented-python",
        "command-line-applications",
        "testing-python-programs",
        "code-quality-maintainability",
        "documentation-publishing",
    ]
    assert [unit["number"] for unit in foundations["units"]] == list(range(16))
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


def test_progress_v6_tracks_unit_challenges_without_legacy_migration() -> None:
    old_storage = {
        "fcpython.progress.v5": json.dumps(
            {
                "schema_version": 5,
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
    "courses/python-foundations/units/python-syntax/challenge"
  ),
  challengeIsLesson: isLessonKey(
    "courses/python-foundations/units/python-syntax/challenge"
  ),
};
})();
"""
    )
    lesson_url = (
        "https://freecampus.github.io/python/courses/python-foundations/units/"
        "python-syntax/values-names-assignment.html"
    )
    lesson_path = (
        "/python/courses/python-foundations/units/python-syntax/"
        "values-names-assignment.html"
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
  oldProgress: JSON.parse(storage.get("fcpython.progress.v5")),
  newProgress: storage.get("fcpython.progress.v6") || null,
}}));
"""
    result = subprocess.run(
        ["node"], input=harness, text=True, capture_output=True, check=True
    )
    observed = json.loads(result.stdout)

    assert observed["state"]["currentKey"] == (
        "courses/python-foundations/units/python-syntax/values-names-assignment"
    )
    assert observed["state"]["lessonId"] == ("python-syntax.values-names-assignment")
    assert observed["state"]["unitChallengeId"] == ("python-syntax.challenge")
    assert observed["state"]["challengeIsLesson"] is False
    assert observed["state"]["progress"] == {"schema_version": 6, "courses": {}}
    assert observed["oldProgress"]["schema_version"] == 5
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


def test_internal_qmd_links_resolve() -> None:
    missing = []
    link_pattern = re.compile(r"\[[^\]]*\]\((?P<target>[^)]+\.qmd(?:#[^)]*)?)\)")

    for page in sorted(Path("docs").rglob("*.qmd")):
        if "_site" in page.parts:
            continue
        for match in link_pattern.finditer(page.read_text()):
            raw_target = match.group("target").split("#", 1)[0]
            target = (page.parent / raw_target).resolve()
            if not target.exists():
                missing.append(f"{page}: {raw_target}")

    assert missing == []
