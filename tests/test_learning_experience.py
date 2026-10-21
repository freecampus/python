import json
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

import yaml

COURSE_IDS = {
    "python-foundations",
    "intermediate-python",
    "advanced-python",
    "scientific-python",
    "statistics-python",
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


def test_numbered_code_wraps_with_quartos_rendered_markup() -> None:
    rendered = subprocess.run(
        ["quarto", "pandoc", "--from", "markdown", "--to", "html"],
        input=(
            "```{.text .numberLines}\n"
            "A deliberately long evidence line that must wrap inside the block.\n"
            "```\n"
        ),
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    styles = Path("docs/styles.css").read_text()

    assert re.search(r'<pre\s+class="sourceCode numberSource\b', rendered)
    code_rule = re.search(
        r"pre\.numberSource\s*>\s*code\.sourceCode\s*\{(?P<body>[^}]*)\}",
        styles,
    )
    line_rule = re.search(
        r"pre\.numberSource\s*>\s*code\.sourceCode\s*>\s*span\s*"
        r"\{(?P<body>[^}]*)\}",
        styles,
    )

    assert code_rule
    assert "white-space: pre-wrap !important;" in code_rule.group("body")
    assert line_rule
    assert "display: inline-block;" in line_rule.group("body")
    assert "overflow-wrap: anywhere;" in line_rule.group("body")
    assert "padding-left: 5em;" in line_rule.group("body")
    assert "text-indent: -5em;" in line_rule.group("body")
    assert "width: calc(100% + 4em);" in line_rule.group("body")
    assert "pre.numberSource.code-overflow-wrap" not in styles


def test_site_footer_identifies_current_curriculum() -> None:
    catalog = _yaml(Path("docs/courses/_catalog.yml"))
    quarto = _yaml(Path("docs/_quarto.yml"))
    updated = date.fromisoformat(catalog["last_updated"])
    display_date = f"{updated.day} {updated.strftime('%B %Y')}"

    assert quarto["website"]["page-footer"]["center"] == (
        f"Course content updated {display_date} · "
        f"Curriculum v{catalog['curriculum_version']}"
    )


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
    assert "markSameOriginLinksInternal" in course_ui
    assert 'link.classList.add("no-external")' in course_ui


def test_course_catalog_is_generated_and_filterable() -> None:
    course_map = Path("docs/courses/index.qmd").read_text()
    template = Path("docs/courses/_listings/course-card.ejs.md").read_text()
    course_ui = Path("docs/_includes/course-ui.html").read_text()

    listing_contents = _front_matter(Path("docs/courses/index.qmd"))["listing"][0][
        "contents"
    ]
    catalog = _yaml(Path("docs/courses/_catalog.yml"))
    assert set(listing_contents) == {
        course["home"].removeprefix("courses/")
        if course["home"].startswith("courses/")
        else "../" + course["home"]
        for course in catalog["courses"]
    }
    assert "template: _listings/course-card.ejs.md" in course_map
    assert "data-fc-catalog-search" in course_map
    assert "data-fc-course-filter" in course_map
    assert 'data-fc-course-filter="statistics"' in course_map
    assert "data-fc-course-card" in template
    assert "data-course-id" in template
    assert "data-course-keywords" in template
    assert "setupCatalog" in course_ui
    assert "pathways.includes(filter)" in course_ui
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


def test_scientific_and_statistics_paths_converge_before_data_ml() -> None:
    courses = _yaml(Path("docs/courses/_catalog.yml"))["courses"]
    by_id = {course["id"]: course for course in courses}

    assert by_id["scientific-python"]["prerequisite_ids"] == ["python-foundations"]
    assert by_id["statistics-python"]["prerequisite_ids"] == ["python-foundations"]
    assert set(by_id["data-science-ml"]["prerequisite_ids"]) == {
        "scientific-python",
        "statistics-python",
    }
    assert by_id["scientific-python"]["recommended_ids"] == []
    assert by_id["statistics-python"]["recommended_ids"] == []
    assert by_id["data-science-ml"]["recommended_ids"] == []

    for path in (
        Path("docs/index.qmd"),
        Path("docs/courses/index.qmd"),
        Path("docs/pathways/index.qmd"),
    ):
        text = path.read_text()
        assert "F --> S" in text
        assert "F --> T" in text
        assert "S --> M" in text
        assert "T --> M" in text
        assert "I -. recommended .-> M" not in text


def test_course_catalog_owns_every_teaching_lesson_once() -> None:
    catalog = _yaml(Path("docs/courses/_catalog.yml"))
    courses = catalog["courses"]
    owned_paths: set[Path] = set()
    lesson_ids: set[str] = set()

    assert catalog["schema_version"] == 2
    assert catalog["curriculum_version"] == 22
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
    assert len(lesson_ids) == 112


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
    retired_get_started_pages = {
        "programming-python-ai.qmd",
        "learning-loop-ai.qmd",
        "notebooks-literate-workflows.qmd",
        "local-python-environment.qmd",
    }
    get_started_root = (
        foundations_root / "milestones" / "first-programs" / "units" / "get-started"
    )
    assert not any(
        (get_started_root / page).exists() for page in retired_get_started_pages
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

    assert len(public_pages) == 137
    assert len(notebook_paths) == 137


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
        assert front_matter["course_pathway"] == course["pathway"]
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

        for milestone in course["milestones"]:
            root = milestone["directory"]
            expected_paths.update({root + "/index.qmd", root + "/challenge.qmd"})
            section = _sidebar_section(
                sidebar["contents"],
                f"Milestone {course['milestones'].index(milestone) + 1}: "
                f"{milestone['title']}",
            )
            milestone_paths = _sidebar_paths(section["contents"])
            assert milestone_paths[0] == root + "/index.qmd"
            assert milestone_paths[-1] == root + "/challenge.qmd"
            assert milestone["unit_ids"] == [
                u["id"] for u in course["units"] if u["milestone_id"] == milestone["id"]
            ]
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

    assert completion["curriculum_version"] == 22
    assert completion["rule_version"] == 13
    assert completion["recognition"] == "local-self-reported"
    assert len(lesson_ids) == foundations["lesson_count"] == 97
    assert home_metadata["lesson_ids"] == completion["lesson_ids"]
    assert progress_ids_match is not None
    assert progress_ids_match.group(1).split() == completion["lesson_ids"]
    assert f"curriculum version {completion['curriculum_version']}" in home_text
    assert "curriculum_version: 22" in course_ui
    assert "state.curriculum_version = 22" in course_ui
    assert "completion_rule_version: 13" in course_ui
    assert "state.completion_rule_version = 13" in course_ui
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
    assert len(foundations["milestones"]) == 4
    assert len(completion["milestone_challenges"]) == 4
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
        Path("docs/courses/python-foundations/milestones").glob(
            "*/units/*/challenge.qmd"
        )
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
            assert "10 of 12" in text
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

    assert foundations["lesson_count"] == 97
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

    intermediate_home = Path("docs/roadmap/intermediate-python/index.qmd").read_text()
    advanced_home = Path("docs/roadmap/advanced-python/index.qmd").read_text()
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
    "courses/python-foundations/milestones/first-programs/units/python-syntax/challenge"
  ),
  challengeIsLesson: isLessonKey(
    "courses/python-foundations/milestones/first-programs/units/python-syntax/challenge"
  ),
};
})();
"""
    )
    lesson_url = (
        "https://freecampus.github.io/python/courses/python-foundations/milestones/first-programs/units/"
        "python-syntax/values-names-assignment.html"
    )
    lesson_path = (
        "/python/courses/python-foundations/milestones/first-programs/units/python-syntax/"
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
        "courses/python-foundations/milestones/first-programs/units/python-syntax/values-names-assignment"
    )
    assert observed["state"]["lessonId"] == ("python-syntax.values-names-assignment")
    assert observed["state"]["unitChallengeId"] == ("python-syntax.challenge")
    assert observed["state"]["challengeIsLesson"] is False
    assert observed["state"]["progress"] == {"schema_version": 6, "courses": {}}
    assert observed["oldProgress"]["schema_version"] == 5
    assert observed["newProgress"] is None


def test_course_continue_uses_recorded_progress_not_the_last_page_visited() -> None:
    course_ui = Path("docs/_includes/course-ui.html").read_text()
    script = course_ui.split("<script>", 1)[1].rsplit("</script>", 1)[0]
    course_home = Path("docs/courses/python-foundations/index.qmd").read_text()
    site = "https://freecampus.github.io/python/"
    overview = (
        f"{site}courses/python-foundations/milestones/first-programs/units/get-started/"
    )
    first_lesson = f"{overview}meet-python-first-program.html"
    second_lesson = f"{overview}learn-with-evidence.html"
    unit_two_lesson = (
        f"{site}courses/python-foundations/milestones/first-programs/units/core-values-types/"
        "values-types-none-conversion.html"
    )
    activities = [
        first_lesson,
        second_lesson,
        f"{overview}challenge.html",
        unit_two_lesson,
    ]

    def render_resume(completed_lessons: dict[str, str]) -> dict[str, str]:
        storage = {
            "fcpython.progress.v6": json.dumps(
                {
                    "schema_version": 6,
                    "courses": {
                        "python-foundations": {
                            "completed_lessons": completed_lessons,
                            "completed_challenges": {},
                        }
                    },
                }
            ),
            "fcpython.last-lesson.v6": json.dumps(
                {
                    "schema_version": 6,
                    "global": None,
                    "courses": {
                        "python-foundations": {
                            "key": (
                                "courses/python-foundations/milestones/first-programs/units/"
                                "core-values-types/values-types-none-conversion"
                            )
                        }
                    },
                }
            ),
        }
        harness = f"""
const storage = new Map(Object.entries({json.dumps(storage)}));
const resumeLink = {{
  dataset: {{fcCourseResume: "python-foundations"}},
  href: {json.dumps(overview)},
  textContent: "Start Unit 0",
}};
const activityLinks = {json.dumps(activities)}.map((href) => ({{href}}));
const sidebar = {{
  querySelector: () => null,
  querySelectorAll: () => activityLinks,
}};
global.window = {{
  location: {{
    href: {json.dumps(f"{site}courses/python-foundations/")},
    pathname: "/python/courses/python-foundations/",
  }},
  localStorage: {{
    getItem: (key) => storage.has(key) ? storage.get(key) : null,
    setItem: (key, value) => storage.set(key, value),
  }},
}};
global.document = {{
  querySelector: (selector) => selector === "#quarto-sidebar" ? sidebar : null,
  querySelectorAll: (selector) =>
    selector === "[data-fc-course-resume]" ? [resumeLink] : [],
  body: {{classList: {{add: () => {{}}}}}},
  title: "Python Foundations",
}};
{script}
process.stdout.write(JSON.stringify(resumeLink));
"""
        result = subprocess.run(
            ["node"], input=harness, text=True, capture_output=True, check=True
        )
        return json.loads(result.stdout)

    not_started = render_resume({})
    in_progress = render_resume(
        {"get-started.meet-python-first-program": "2026-08-05T00:00:00Z"}
    )

    assert (
        "[Start Unit 0](milestones/first-programs/units/get-started/index.qmd)"
        in course_home
    )
    assert not_started == {
        "dataset": {"fcCourseResume": "python-foundations"},
        "href": overview,
        "textContent": "Start Unit 0",
    }
    assert in_progress["href"] == second_lesson
    assert in_progress["textContent"] == "Continue course"


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


def test_journey_sources_and_notebooks_follow_milestone_ownership() -> None:
    catalog = _yaml(Path("docs/courses/_catalog.yml"))
    quarto = _yaml(Path("docs/_quarto.yml"))
    assert quarto["freecampus"] == {"schema-version": 1, "kind": "journey"}
    published = [course for course in catalog["courses"] if course["units"]]
    planned = [course for course in catalog["courses"] if not course["units"]]
    assert len(published) == 3
    assert len(planned) == 3
    assert sum(len(course["milestones"]) for course in published) == 7
    for course in planned:
        assert course["home"] == f"roadmap/{course['id']}/index.qmd"
        assert not (Path("docs/courses") / course["id"]).exists()
    for course in published:
        completion = course["completion"]
        home = Path("docs") / course["home"]
        challenge_ids = [
            challenge["id"]
            for challenge in completion["challenges"]
            + completion["milestone_challenges"]
        ]
        assert len(challenge_ids) == len(set(challenge_ids))
        assert _front_matter(home)["challenge_ids"] == challenge_ids
        assert (
            f'data-course-challenge-ids="{" ".join(challenge_ids)}"' in home.read_text()
        )
        assert not (home.parent / "units").exists()
        for milestone in course["milestones"]:
            root = Path("docs") / milestone["directory"]
            overview = root / "index.qmd"
            challenge = root / "challenge.qmd"
            assert "quiz-config" not in overview.read_text()
            assert _front_matter(challenge)["assessment_type"] == "milestone-challenge"
            assert (
                _front_matter(challenge)["challenge_id"]
                == milestone["id"] + ".challenge"
            )
            assert "data-fc-challenge-complete" in challenge.read_text()
            for page in root.rglob("*.qmd"):
                expected = (
                    "notebooks/"
                    + page.relative_to("docs").with_suffix(".ipynb").as_posix()
                )
                assert _front_matter(page)["colab_notebook"] == expected
                for include in re.findall(
                    r"\{\{< include (\S+) >\}\}", page.read_text()
                ):
                    assert (page.parent / include).is_file(), (page, include)


def test_milestone_progress_preserves_records_and_requires_integration_challenges() -> (
    None
):
    course = next(
        c
        for c in _yaml(Path("docs/courses/_catalog.yml"))["courses"]
        if c["id"] == "python-foundations"
    )
    completion = course["completion"]
    unit_ids = [c["id"] for c in completion["challenges"]]
    milestone_ids = [c["id"] for c in completion["milestone_challenges"]]
    saved = {
        "schema_version": 6,
        "courses": {
            "python-foundations": {
                "curriculum_version": 21,
                "completion_rule_version": 12,
                "completed_lessons": dict.fromkeys(completion["lesson_ids"], "saved"),
                "completed_challenges": dict.fromkeys(unit_ids, "saved"),
            }
        },
    }
    script = (
        Path("docs/_includes/course-ui.html")
        .read_text()
        .split("<script>", 1)[1]
        .rsplit("</script>", 1)[0]
    )
    script = (
        script.rsplit("})();", 1)[0]
        + """
window.__fcTest = {completionSnapshot, courseState, isLessonKey, challengeIdFromKey};
})();
"""
    )
    dataset = {
        "courseLessonIds": " ".join(completion["lesson_ids"]),
        "courseChallengeIds": " ".join(unit_ids + milestone_ids),
    }
    harness = f"""
const saved = {json.dumps(saved)};
global.window = {{
  location: {{
    href: "https://freecampus.org/python/courses/python-foundations/",
    pathname: "/python/courses/python-foundations/",
  }},
  localStorage: {{
    getItem: (key) => key === "fcpython.progress.v6" ? JSON.stringify(saved) : null,
    setItem: () => {{}},
  }},
}};
global.document = {{
  querySelector: () => null, querySelectorAll: () => [],
  body: {{classList: {{add: () => {{}}}}}}, title: "Foundations",
}};
{script}
const api = window.__fcTest;
const root = {{dataset: {json.dumps(dataset)}}};
const before = api.completionSnapshot(root, "python-foundations");
const state = api.courseState("python-foundations");
for (const id of {json.dumps(milestone_ids)}) state.completed_challenges[id] = "new";
const base = "courses/python-foundations/milestones/first-programs";
process.stdout.write(JSON.stringify({{
  before, after: api.completionSnapshot(root, "python-foundations"),
  lessonRecord: state.completed_lessons["python-syntax.values-names-assignment"],
  unitRecord: state.completed_challenges["python-syntax.challenge"],
  overviewIsLesson: api.isLessonKey(base),
  unitOverviewIsLesson: api.isLessonKey(base + "/units/python-syntax"),
  challengeIsLesson: api.isLessonKey(base + "/challenge"),
  milestoneId: api.challengeIdFromKey(base + "/challenge"),
}}));
"""
    result = subprocess.run(
        ["node"], input=harness, text=True, capture_output=True, check=True
    )
    observed = json.loads(result.stdout)
    assert observed["before"]["completed"] == 113
    assert observed["before"]["total"] == observed["after"]["completed"] == 117
    assert observed["lessonRecord"] == observed["unitRecord"] == "saved"
    assert observed["milestoneId"] == "first-programs.challenge"
    assert not observed["overviewIsLesson"]
    assert not observed["unitOverviewIsLesson"]
    assert not observed["challengeIsLesson"]


def test_foundations_expandable_units_preserve_the_full_learning_sequence() -> None:
    home = Path("docs/courses/python-foundations/index.qmd").read_text()
    catalog = yaml.safe_load(Path("docs/courses/_catalog.yml").read_text())
    course = next(c for c in catalog["courses"] if c["id"] == "python-foundations")
    rows = re.findall(
        r'<details class="fc-unit-row">(.*?)</details>', home, flags=re.DOTALL
    )
    assert len(rows) == len(course["units"])
    for row, unit in zip(rows, course["units"], strict=True):
        directory = Path("docs") / unit["directory"]
        lessons = sorted(
            (
                (_front_matter(path)["lesson_order"], path)
                for path in directory.glob("*.qmd")
                if "lesson_id" in _front_matter(path)
            ),
        )
        linked_lessons = re.findall(r"^\d+\. \[.*?\]\((.*?)\)", row, re.MULTILINE)
        assert linked_lessons == [
            f"milestones/{unit['milestone_id']}/units/{unit['id']}/{path.name}"
            for _, path in lessons
        ]
        assert f"{len(lessons)} lessons</span>" in row
        assert f"milestones/{unit['milestone_id']}/units/{unit['id']}/index.qmd" in row
        assert (
            f"milestones/{unit['milestone_id']}/units/{unit['id']}/challenge.qmd" in row
        )
