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
    assert "$module_id$" in title_block
    assert "$lesson_id$" in title_block
    assert "$checkpoint_id$" in title_block
    assert "$project_id$" in title_block
    assert "$completion_label$" in title_block
    assert "data-fc-complete" in title_block
    assert "data-fc-lesson-progress" in title_block
    assert "fcpython.progress.v2" in course_ui
    assert "fcpython.last-lesson.v2" in course_ui
    assert "legacyProgressKey" in course_ui
    assert "lessonIdFromKey" in course_ui
    assert "completed_checkpoints" in course_ui
    assert "capstone_status" in course_ui
    assert "completionSnapshot" in course_ui
    assert "setupCheckpointButton" in course_ui
    assert "setupProjectButton" in course_ui
    assert "migrateCourseOwnership" in course_ui
    assert "migrateLastLessonOwnership" in course_ui
    assert "isOptionalSidebarLink" in course_ui
    assert 'label?.includes("optional")' in course_ui
    assert "chapterLessonCounts" not in course_ui


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
    courses = _yaml(Path("docs/courses/_catalog.yml"))["courses"]
    owned_paths: set[Path] = set()
    lesson_ids: set[str] = set()

    for course in courses:
        course_total = 0
        for module in course["modules"]:
            directory = Path("docs") / module["directory"]
            metadata = _yaml(directory / "_metadata.yml")
            pages = sorted(
                (
                    path
                    for path in directory.glob("*.qmd")
                    if path.name != "index.qmd" and _front_matter(path).get("lesson_id")
                ),
                key=lambda path: _front_matter(path)["lesson_order"],
            )

            assert metadata["course_id"] == course["id"]
            assert metadata["module_id"] == module["id"]
            assert len(pages) == module["lesson_count"]
            assert len({_front_matter(path)["lesson_order"] for path in pages}) == len(
                pages
            )

            for path in pages:
                front_matter = _front_matter(path)
                lesson_id = front_matter["lesson_id"]
                assert lesson_id.startswith(f"{module['id']}.")
                assert lesson_id not in lesson_ids
                assert path not in owned_paths
                lesson_ids.add(lesson_id)
                owned_paths.add(path)
            course_total += len(pages)

        assert course_total == course["lesson_count"]

    expected = {
        path
        for path in Path("docs/courses").rglob("*.qmd")
        if _front_matter(path).get("lesson_id")
    }
    assert owned_paths == expected
    assert len(lesson_ids) == 53


def test_course_source_migration_preserves_legacy_public_urls() -> None:
    assert not Path("docs/lessons").exists()

    public_pages = []
    aliases: set[str] = set()
    for root in (Path("docs/courses"), Path("docs/resources")):
        for path in root.rglob("*.qmd"):
            front_matter = _front_matter(path)
            notebook = front_matter.get("colab_notebook")
            if not notebook:
                continue

            public_pages.append(path)
            page_aliases = set(front_matter.get("aliases", []))
            legacy_alias = (
                f"/{notebook.removeprefix('notebooks/').removesuffix('.ipynb')}.html"
            )
            expected_aliases = {legacy_alias}
            foundations_root = Path("docs/courses/python-foundations")
            if path.is_relative_to(foundations_root):
                relative = path.relative_to(foundations_root)
                previous_owner = {
                    "files-and-data": "intermediate-python",
                    "projects-and-environments": "intermediate-python",
                    "code-quality": "intermediate-python",
                    "object-oriented-python": "intermediate-python",
                    "advanced-python-patterns": "advanced-python",
                }.get(relative.parts[0])
                if previous_owner:
                    previous_path = relative.with_suffix(".html").as_posix()
                    expected_aliases.add(f"/courses/{previous_owner}/{previous_path}")

            assert page_aliases == expected_aliases, path
            assert aliases.isdisjoint(page_aliases), path
            aliases.update(page_aliases)

    course_catalog = _front_matter(Path("docs/courses/index.qmd"))
    assert course_catalog["aliases"] == ["/lessons/index.html"]
    assert course_catalog["legacy_colab_notebook"] == "notebooks/lessons/index.ipynb"
    assert len(public_pages) == 82
    assert len(aliases) == 106


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
        previous_module_position = 0

        checkpoints_by_module = {
            checkpoint["id"]: checkpoint
            for checkpoint in course.get("completion", {}).get("checkpoints", [])
        }

        for module in course["modules"]:
            directory = Path(module["directory"])
            module_root = Path("docs") / directory
            module_home = module_root / "index.qmd"
            module_navigation = _sidebar_section(sidebar["contents"], module["title"])
            pages = sorted(
                (
                    path
                    for path in module_root.glob("*.qmd")
                    if path.name != "index.qmd" and _front_matter(path).get("lesson_id")
                ),
                key=lambda path: _front_matter(path)["lesson_order"],
            )
            assert _front_matter(module_home)["title"] == f"{module['title']} Overview"
            assert module_navigation["contents"][0] == {
                "href": (directory / "index.qmd").as_posix(),
                "text": "Overview",
            }
            module_paths = [(directory / "index.qmd").as_posix()]
            module_paths.extend(path.relative_to("docs").as_posix() for path in pages)
            if module["id"] in checkpoints_by_module:
                module_paths.append(checkpoints_by_module[module["id"]]["path"])
            module_position = sidebar_paths.index(module_paths[0])
            assert module_position > previous_module_position
            assert sidebar_paths[
                module_position : module_position + len(module_paths)
            ] == (module_paths)
            previous_module_position = module_position
            expected_paths.update(module_paths)

        project = course.get("completion", {}).get("project")
        if project:
            expected_paths.add(project["path"])

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

    assert completion["curriculum_version"] == 1
    assert completion["rule_version"] == 1
    assert completion["recognition"] == "local-self-reported"
    assert len(required) == foundations["required_lesson_count"] == 18
    assert len(optional) == foundations["optional_lesson_count"] == 20
    assert required.isdisjoint(optional)

    metadata_by_id = {}
    for module in foundations["modules"]:
        directory = Path("docs") / module["directory"]
        for path in directory.glob("*.qmd"):
            front_matter = _front_matter(path)
            if lesson_id := front_matter.get("lesson_id"):
                metadata_by_id[lesson_id] = front_matter

    assert set(metadata_by_id) == required | optional
    for lesson_id in required:
        assert metadata_by_id[lesson_id]["required_for_completion"] is True
        assert metadata_by_id[lesson_id]["completion_label"] == "Required lesson"
    for lesson_id in optional:
        assert metadata_by_id[lesson_id]["required_for_completion"] is False
        assert metadata_by_id[lesson_id]["completion_label"] == "Optional lesson"

    checkpoints = completion["checkpoints"]
    assert len(checkpoints) == 5
    assert {checkpoint["id"] for checkpoint in checkpoints} == {
        "getting-started",
        "core-python",
        "data-structures",
        "functions",
        "debugging",
    }
    for checkpoint in checkpoints:
        path = Path("docs") / checkpoint["path"]
        front_matter = _front_matter(path)
        assert path.exists()
        assert checkpoint["required"] is True
        assert front_matter["checkpoint_id"] == checkpoint["id"]
        assert front_matter["assessment_type"] == "module-checkpoint"
        assert front_matter["required_for_completion"] is True

    project = completion["project"]
    project_path = Path("docs") / project["path"]
    project_front_matter = _front_matter(project_path)
    project_text = project_path.read_text()
    assert project_front_matter["project_id"] == project["id"]
    assert project_front_matter["rubric_version"] == project["rubric_version"]
    assert project_front_matter["required_for_completion"] is True
    assert "| Criterion | Not yet | Meets the requirement |" in project_text
    assert "not a submission" in project_text.lower()


def test_software_courses_use_problem_complexity_as_the_level_boundary() -> None:
    courses = _yaml(Path("docs/courses/_catalog.yml"))["courses"]
    by_id = {course["id"]: course for course in courses}
    foundations = by_id["python-foundations"]
    intermediate = by_id["intermediate-python"]
    advanced = by_id["advanced-python"]

    assert foundations["lesson_count"] == 38
    assert {module["id"] for module in foundations["modules"]} >= {
        "files-and-data",
        "projects-and-environments",
        "code-quality",
        "object-oriented-python",
        "advanced-python-patterns",
    }
    assert intermediate["title"] == "Intermediate Python: Applied Problem Solving"
    assert advanced["title"] == "Advanced Python: Complex Problem Solving"
    assert not Path("docs/courses/intermediate-python/files-and-data").exists()
    assert not Path("docs/courses/advanced-python/advanced-python-patterns").exists()
    for course in (intermediate, advanced):
        assert course["status"] == "in-development"
        assert course["lesson_count"] == 0
        assert course["modules"] == []
        assert course["estimated_effort"] == "TBD"

    intermediate_home = Path("docs/courses/intermediate-python/index.qmd").read_text()
    advanced_home = Path("docs/courses/advanced-python/index.qmd").read_text()
    assert "progressively harder problems" in intermediate_home
    assert "Planned challenge format" in intermediate_home
    assert re.search(r"complex problems under\s+real\s+constraints", advanced_home)
    assert "Planned challenge format" in advanced_home


def test_retired_course_progress_moves_to_foundations() -> None:
    progress = {
        "schema_version": 2,
        "courses": {
            "python-foundations": {
                "completed_lessons": {
                    "core-python.values-variables-types": "foundation-original"
                }
            },
            "intermediate-python": {
                "completed_lessons": {
                    "files-and-data.paths-and-text-files": "from-intermediate",
                    "future-problems.challenge-one": "keep-for-future",
                }
            },
            "advanced-python": {
                "completed_lessons": {
                    "advanced-python-patterns.decorators": "from-advanced"
                }
            },
        },
    }
    last_lesson = {
        "schema_version": 2,
        "global": {
            "key": "courses/advanced-python/advanced-python-patterns/decorators",
            "course_id": "advanced-python",
            "lesson_id": "advanced-python-patterns.decorators",
            "title": "Decorators",
        },
        "courses": {
            "intermediate-python": {
                "key": (
                    "courses/intermediate-python/files-and-data/paths-and-text-files"
                ),
                "course_id": "intermediate-python",
                "lesson_id": "files-and-data.paths-and-text-files",
                "title": "Paths and Text Files",
            },
            "advanced-python": {
                "key": "courses/advanced-python/advanced-python-patterns/decorators",
                "course_id": "advanced-python",
                "lesson_id": "advanced-python-patterns.decorators",
                "title": "Decorators",
            },
        },
    }
    storage = {
        "fcpython.progress.v2": json.dumps(progress),
        "fcpython.last-lesson.v2": json.dumps(last_lesson),
    }
    course_ui = Path("docs/_includes/course-ui.html").read_text()
    script = course_ui.split("<script>", 1)[1].rsplit("</script>", 1)[0]
    harness = f"""
const storage = new Map(Object.entries({json.dumps(storage)}));
global.window = {{
  location: {{
    href: "https://freecampus.github.io/python/courses/index.html",
    pathname: "/python/courses/index.html",
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
  title: "FreeCampus Python",
}};
{script}
process.stdout.write(JSON.stringify({{
  progress: JSON.parse(storage.get("fcpython.progress.v2")),
  lastLesson: JSON.parse(storage.get("fcpython.last-lesson.v2")),
}}));
"""
    result = subprocess.run(
        ["node"], input=harness, text=True, capture_output=True, check=True
    )
    migrated = json.loads(result.stdout)
    courses = migrated["progress"]["courses"]
    foundation_lessons = courses["python-foundations"]["completed_lessons"]

    assert foundation_lessons["core-python.values-variables-types"] == (
        "foundation-original"
    )
    assert foundation_lessons["files-and-data.paths-and-text-files"] == (
        "from-intermediate"
    )
    assert foundation_lessons["advanced-python-patterns.decorators"] == (
        "from-advanced"
    )
    assert courses["intermediate-python"]["completed_lessons"] == {
        "future-problems.challenge-one": "keep-for-future"
    }
    assert courses["advanced-python"]["completed_lessons"] == {}

    migrated_last = migrated["lastLesson"]
    assert migrated_last["global"]["course_id"] == "python-foundations"
    assert migrated_last["global"]["key"] == (
        "courses/python-foundations/advanced-python-patterns/decorators"
    )
    assert set(migrated_last["courses"]) == {"python-foundations"}
    assert migrated_last["courses"]["python-foundations"] == migrated_last["global"]


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
