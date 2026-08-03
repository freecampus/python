# AGENTS.md

Guidance for AI agents and maintainers working in this repository.

## Repository purpose

FreeCampus Python is a beginner-first portfolio of connected Python courses for
learners ranging from zero programming experience to advanced, scientific, and
machine-learning work. The public product is a Quarto website. A small Python
package supports reusable quiz models and notebook widgets.

The teaching goal is **zero to practical project confidence**. Learners should
repeatedly read, predict, run, trace, explain, modify, check, and debug real
Python before moving on.

## Local-first workflow

- Inspect the local workspace before considering any remote source.
- Do not plan, review, or implement from the GitHub tree when the local checkout
  is available; local branch state may differ.
- Check `git status --short` before and after edits. Preserve unrelated user
  work and never clean or reset it away.
- For non-trivial work, give a short implementation plan and wait for approval
  unless the user explicitly requests direct implementation.
- `PLAN.md` is ignored by git and is local planning material. When work is
  driven by it, update its status and any implementation deviations before
  handoff.
- Prefer the simplest non-login, non-interactive local read command if normal
  shell access has a problem. State the limitation before using a remote
  fallback.
- Do not create commits, push, or open pull requests unless explicitly asked.

## Project layout and sources of truth

```text
.
├── docs/
│   ├── index.qmd                         # Portfolio home
│   ├── _quarto.yml                       # Navbar and all course sidebars
│   ├── _brand.yml                        # Shared visual brand
│   ├── styles.css                        # Global course and quiz styling
│   ├── components/                       # Focused responsive/site CSS
│   ├── _includes/                        # Shared quiz, Colab, and course UI
│   ├── _partials/                        # Quarto title template
│   ├── _templates/                       # Authoring scaffolds
│   ├── courses/
│   │   ├── _catalog.yml                  # Canonical course/unit ownership
│   │   ├── python-foundations/
│   │   │   ├── _outcomes.yml             # Unit-to-outcome map
│   │   │   └── units/<unit-id>/          # Overview, lessons, challenge
│   │   ├── intermediate-python/
│   │   ├── advanced-python/
│   │   ├── scientific-python/
│   │   └── data-science-ml/
│   ├── pathways/                         # Cross-course pathway guidance
│   └── resources/                        # FAQ and project/support material
├── notebooks/                            # Hand-maintained notebook examples
├── scripts/build_colab_notebooks.py      # QMD-to-Colab generator
├── src/fcpython/                         # Quiz models, banks, widgets
├── tests/                                # Package and curriculum invariants
├── .github/workflows/                    # CI and documentation publishing
├── .makim.yaml                           # Local task runner
└── pyproject.toml
```

Use these sources together:

- QMD files are the teaching-content source of truth.
- `docs/courses/_catalog.yml` owns course titles, units, lesson counts,
  completion lesson IDs, challenge records, status, and estimated effort.
- Each unit's `_metadata.yml` supplies inherited course/unit identity.
- `docs/courses/python-foundations/_outcomes.yml` maps every Foundations lesson
  and challenge to unit and graduate outcomes.
- `docs/_quarto.yml` owns visible sidebar order.
- A course home repeats progress-facing counts and IDs in front matter and HTML
  data attributes. Keep those values synchronized with the catalog.
- Tests intentionally enforce many of these relationships. Update the source
  records and their invariant tests together; do not weaken a test merely to
  hide an inconsistent curriculum.

## Course portfolio and pathway rules

- Every teaching lesson belongs to exactly one catalog course and unit. Shared
  FAQ, pathway, and project-toolkit pages do not count toward course completion.
- Use `course_id`, `unit_id`, `lesson_id`, `challenge_id`, and `project_id` as
  machine identities, not display titles.
- A content lesson's `lesson_id` starts with its unit ID. Use stable increments
  such as `lesson_order: 10`, `20`, and `30`; reserve `order: 90` for the unit
  challenge.
- Current Python Foundations lessons and unit challenges form one required
  sequence. Do not add “required,” “optional,” or completion flags to individual
  lesson front matter or visible lesson copy.
- Every instructional Foundations unit has an Overview first and a Unit
  Challenge last. Sidebar labels use a colon: `Unit N: Unit Title`.
- Unit overview titles follow `Unit Title Overview`; their sidebar text remains
  `Overview`.
- Foundations owns the Python language, essential tooling, OOP, testing,
  packaging, documentation, and reusable patterns.
- Intermediate is planned as applied problem solving with unfamiliar,
  progressively harder problems. Advanced is planned around complex state,
  search, constraints, performance, architecture, concurrency, and defensible
  trade-offs.
- Do not repopulate Intermediate or Advanced with Foundations topic checklists.
  Keep them in development until problem-driven lessons, assessments, and
  completion rules exist.
- Scientific Python and Data Science/Machine Learning may require Foundations
  and may recommend each other only through valid, acyclic catalog IDs.
- Browser progress is local and self-reported. Do not describe it as verified
  assessment or certificate evidence. The final project and certificate are
  planned but not currently available.

## Curriculum migrations and compatibility

The portfolio is still undergoing intentional pre-release curriculum resets. Do
not preserve obsolete routes automatically.

For an approved route, ID, or lesson-structure migration:

1. remove the old page rather than keeping duplicate teaching content;
2. update the unit sidebar in `docs/_quarto.yml`;
3. update catalog lesson IDs, counts, unit titles, effort, and challenge titles;
4. update `_outcomes.yml`;
5. update the course home's front matter, progress data attributes, counts, and
   learning-sequence table;
6. update unit `_metadata.yml`;
7. update FAQ, resource, and pathway links;
8. update generated-notebook paths;
9. update structural tests that intentionally assert the new public map;
10. search the repository for every retired path, ID, and title.

If the user explicitly requires compatibility for a published route or learner
progress, design and test aliases, stable IDs, schema/version changes, and any
progress migration instead of assuming a reset.

## Premium lesson standard

Keep lessons cohesive, but do not confuse cohesion with brevity. A foundational
topic needs enough depth for a learner to use it in several contexts.

The rebuilt Unit 1 pages under
`docs/courses/python-foundations/units/python-syntax/` are the current
benchmark:

- the shorter substantive lessons contain roughly 2,900–3,100 instructional
  words and 37–63 runnable examples or repair cases;
- the indentation lesson is a deeper reference lab with about 4,600 words and
  many focused failures;
- each major lesson uses several topic-specific quiz checkpoints;
- richness comes from use, tracing, modification, debugging, and explanation,
  not from repeated prose.

These figures are orientation, not quotas. A narrower lesson may be shorter.
However, a 500–700 word page with two examples and a generic exercise is usually
too superficial for a core Foundations topic.

A substantial lesson should normally include:

- one concrete task or artifact that gives the page a through-line;
- 3–5 learner questions stated near the beginning;
- several distinct uses of the concept;
- multiple correct examples and realistic failure cases;
- line-by-line explanations at the moment a beginner needs them;
- prediction, trace-table, annotation, or dependency-reading work;
- small controlled modifications with expected effects;
- debugging practice using exact output or error evidence;
- at least one hidden hint or solution path;
- 2–3 short checkpoints when the page has several concept groups;
- a final lab or integration task with observable checks;
- key points and descriptive links to primary documentation.

Do not pad a lesson to reach a word count. Every section and example must help
the learner perform, explain, or repair something.

Treat this guide and the recent Unit 1 lessons as authoritative when an older
authoring template still contains generic boilerplate. Do not copy obsolete
template headings into new content; update the template when the task includes
template maintenance.

## Scope and prerequisite discipline

- Teach one new conceptual layer at a time.
- Do not make an early lesson depend silently on later concepts such as
  exception handling, `compile()`, `exec()`, namespace dictionaries, classes, or
  advanced collection behavior.
- A later construct may appear as a **clearly labeled preview** when its visible
  shape is the current topic. Explain exactly what the learner needs and name
  the later unit that teaches its behavior.
- Keep detailed types and conversion in the values/types unit, collections in
  the collections unit, control-flow semantics in decisions/repetition, function
  design in the functions unit, and comprehensive documentation in the
  documentation unit.
- When one page combines unrelated topics so tightly that each remains shallow,
  split it into a few cohesive lessons. Do not split a single coherent topic
  into microscopic pages.
- Make time estimates reflect active work—typing, predicting, quizzes, labs, and
  debugging—not silent reading speed.

## Voice and heading patterns

Write for a person with little or no programming experience. Use ordinary
language before formal vocabulary, then use the vocabulary precisely.

Avoid generic or generated-sounding headings, including:

- `The problem this lesson solves`
- `Read and predict a complete case`
- `Investigate the important boundary`
- `Practice from prediction to explanation`
- `Mental model`
- `Tiny example`
- vague `Walkthrough`
- repeated `Example 1`, `Example 2` labels without a meaningful description
- `Step-by-step explanation` when a specific heading is available

Prefer concrete headings that reveal the code or task:

- `## 1. Assignment evaluates the right side first`
- `## 2. Which lines create each value?`
- `## 3. What happens when a name is missing?`
- `## 4. Build a three-item receipt`
- `### What Python does on each line`
- `### Move return into the loop and predict the effect`
- `### Pair every opening and closing delimiter`

Use clean numbered major sections such as `## 1. Strings are text values`, not
`## Section 1: Strings`. Standard headings such as `Common mistake`,
`Check your understanding`, and `Key points` are useful when their content is
specific.

Prefer direct sentences over repeated abstractions about “capabilities,”
“artifacts,” “evidence,” and “boundaries.” Those terms are fine when they name a
specific capability, artifact, observation, or boundary.

## Hands-on teaching patterns

Use a varied set of learning methods instead of repeating one generic practice
section on every page:

- predict an output or error before running;
- trace name-to-value state in a table;
- annotate tokens, delimiters, dependencies, or indentation levels;
- explain what each line reads, creates, changes, returns, displays, or raises;
- make one controlled modification and identify every downstream effect;
- compare two valid implementations and discuss readability;
- repair the earliest failure one change at a time;
- test a changed requirement after the ordinary example passes;
- restart and run from the top to expose hidden notebook state;
- explain the finished program to a future reader.

Name each exercise after its actual task, such as
`Build a transparent event budget` or `Run a mixed syntax-error clinic`.

Prefer Quarto callouts for ordinary notes, tips, warnings, important points, and
practice prompts. Reserve custom CSS classes for real course components such as
`.lesson-meta`, quiz wrappers, completion controls, and concept diagrams.

## Lesson metadata and page structure

A Foundations content lesson normally has:

```yaml
---
title: Concrete Lesson Title
lesson_id: unit-id.lesson-slug
lesson_order: 10
description: One unique, observable lesson description.
execute:
  echo: true
categories:
  - python-foundations
  - unit-id
  - topic
order: 10
colab_notebook: notebooks/courses/python-foundations/units/unit-id/lesson-slug.ipynb
course_id: python-foundations
unit_id: unit-id
unit_number: 1
---
```

Then add a compact metadata block:

```markdown
::: {.lesson-meta}

- **Level:** Beginner
- **Estimated time:** 2–3 hours
- **You will learn:** One concrete learner outcome.
- **Practice in:** Google Colab, JupyterLab, or a local editor :::
```

Requirements:

- Make descriptions, outcomes, and estimates unique to the page.
- Include `categories`, `order`, and an explicit `colab_notebook`.
- Content pages have `lesson_id` and `lesson_order`.
- Challenges have `challenge_id` and assessment metadata, not `lesson_id`.
- Unit overviews do not have a lesson ID or quiz.
- Foundations unit overview pages keep the `fcpython-chapter-lab: start` and
  `fcpython-chapter-lab: end` markers used by structural tests.
- Include the shared Colab launcher on every public lesson, overview, challenge,
  and supported resource page.
- Finish content lessons with key points and descriptive Markdown links rather
  than bare URLs.

## Quizzes

Browser lesson quizzes use static JSON followed by the shared OJS include:

```html
<script type="application/json" class="fcpython-ojs-quiz-config">
  {
    "id": "unique-page-checkpoint-id",
    "title": "Specific checkpoint title",
    "instructions": "Choose the best answer for each question.",
    "questions": []
  }
</script>
```

The shared renderer is `docs/_includes/ojs-quiz.qmd`. It already provides a
compact one-question-at-a-time stepper:

- numbered question tabs;
- Previous and Next Question navigation;
- Next Question appears after a selection rather than changing screens
  immediately;
- Check Answers appears on the final question;
- answered, correct, incorrect, and unanswered tab states;
- return to the first question needing review;
- Arrow, Home, and End keyboard navigation;
- reset, score, focus, and accessible live feedback.

Do not duplicate this JavaScript in individual pages or auto-advance on a radio
selection. Author only the JSON payload and include the renderer.

Quiz authoring rules:

- Every public content lesson, challenge, and assessable support page has at
  least one quiz config and OJS include.
- Foundations unit overview pages remain quiz-free.
- Long lessons should use 2–3 smaller checkpoints near the concepts they assess
  rather than one oversized final quiz.
- Give every quiz and question a unique stable ID.
- Use four plausible options unless a topic clearly requires another shape.
- Rotate correct answer positions across `0`, `1`, `2`, and `3`; tests monitor
  site-wide answer-position bias.
- Build distractors from real misconceptions in the immediately preceding
  content.
- Explanations should teach why the answer fits the code.
- Do not ask generic questions about study methodology when the checkpoint is
  supposed to assess Python.
- Keep the payload valid JSON. The shared include renders the next unrendered
  config, so place an include after each config.

Reusable widget-oriented quiz data belongs in `src/fcpython/quiz_banks.py`. Quiz
models live in `src/fcpython/questions.py`; ipywidgets rendering lives in
`src/fcpython/widgets.py`.

Quiz spacing and stepper presentation belong in the `.fcpython-quiz*` selectors
in `docs/styles.css`. Preserve compact empty-feedback behavior and reasonable
button targets when adjusting layout.

## Unit overviews and challenges

### Unit overviews

An overview is orientation, not another assessment. It should:

- state what the learner will be able to do;
- preview one concrete artifact or scenario;
- show the lesson sequence and purpose of each step;
- identify prerequisites and workspace setup;
- give an honest active-time estimate and suggested stopping points;
- link forward to the first lesson;
- include Colab but no OJS quiz.

### Unit challenges

Every instructional Foundations unit ends with `challenge.qmd`. Unit 0 is the
special quiz-format onboarding challenge. Other unit challenges use the
guided-programming pattern enforced by tests:

- `assessment_type: unit-challenge`
- `challenge_format: guided-programming`
- `estimated_time: 60–120 minutes`
- `<!-- fcpython-unit-challenge: practical -->`
- `## 3. Start from the contract`
- `## 5. Run progressive assertions`
- `## 6. Use the hint ladder only when needed`
- exactly three `<summary>Hint ...</summary>` levels
- `## 7. Keep debugging evidence`
- a hidden solution path;
- an artifact-specific OJS quiz;
- the `data-fc-challenge-complete` self-report control.

Challenges should provide required names, signatures, or docstrings where they
prevent blank-page confusion; progressive assertions; an ordinary example; an
important boundary or changed requirement; and one debugging record. They should
be substantial enough for roughly one to two hours.

Make challenges enjoyable as well as rigorous. Prefer a small puzzle, game,
mystery, simulation, playful tool, or creative artifact over a routine business
form when the unit outcomes allow it. The theme must create an interesting goal
and satisfying result, not merely rename ordinary variables. Vary the scenarios
across units so the course does not become a sequence of invoices and record
processors.

A Foundations learner should be able to solve the challenge independently in
about two hours after completing the unit. Keep domain rules self-contained,
avoid trivia and hidden conceptual leaps, and do not require material from later
units. Create visible progress through small stages, progressive assertions, and
the three-level hint ladder. Supply names, signatures, docstrings, example data,
or partial structure when they reduce blank-page confusion without giving away
the central decisions.

Choose the page title after the scenario and mechanic are clear. A challenge
does not need a new title merely to sound different; rename it only when the new
title describes the artifact better or makes the invitation more engaging. Keep
the sidebar label `Unit Challenge` regardless of the page title.

Do not expose advanced harness machinery merely to test beginner syntax. Do not
label a challenge “required”; the current course sequence already establishes
that.

## Python code and intentional failures

- Use four spaces per indentation level and never mix tabs and spaces in normal
  examples.
- Every normal Python fence must parse.
- Place this marker immediately before a deliberately invalid Python fence:

  ```html
  <!-- fcpython-intentional-invalid-python -->
  ```

- Do not add the marker to valid-but-wrong runtime or logic examples; tests flag
  unnecessary markers.
- Show the expected output or error when it helps the learner verify a
  prediction.
- Explain a failure before presenting the fix.
- Keep assertions aligned with the stated contract. Never edit expected values
  only to manufacture a pass.
- Quarto execution is globally disabled with `execute.eval: false`. Do not rely
  on a live Python kernel during documentation builds.

## Includes and relative paths

Shared files:

- OJS quiz renderer: `docs/_includes/ojs-quiz.qmd`
- Colab launcher: `docs/_includes/colab-link.qmd`
- Browser course/progress UI: `docs/_includes/course-ui.html`

For Python Foundations pages under
`docs/courses/python-foundations/units/<unit-id>/`:

```markdown
{{< include ../../../../_includes/colab-link.qmd >}}
{{< include ../../../../_includes/ojs-quiz.qmd >}}
```

For pages under `docs/courses/<course-id>/<unit-id>/`:

```markdown
{{< include ../../../_includes/colab-link.qmd >}}
{{< include ../../../_includes/ojs-quiz.qmd >}}
```

For pages under `docs/resources/<resource-id>/`:

```markdown
{{< include ../../_includes/colab-link.qmd >}}
{{< include ../../_includes/ojs-quiz.qmd >}}
```

For a page directly under `docs/resources/`:

```markdown
{{< include ../_includes/colab-link.qmd >}}
{{< include ../_includes/ojs-quiz.qmd >}}
```

Calculate paths from the actual page depth instead of copying an example
blindly.

## Mermaid diagrams

Use Mermaid selectively when spatial structure clarifies a concept, such as
bindings, execution order, blocks, control flow, collections, tracebacks,
environments, OOP relationships, decorators, or ML workflows.

Use this form:

````markdown
::: {.concept-diagram} Explain in one sentence what the learner should notice.

```{mermaid}
%%| echo: false
%%| eval: true
flowchart LR
  A[Input] --> B[Process] --> C[Output]
```

:::
````

Both `%%|` options are required because global execution is disabled. Keep node
labels simple and quote labels containing punctuation that Mermaid may parse
ambiguously.

## Colab notebook generation

QMD content under `docs/courses/` and `docs/resources/` is the source of truth.
After Quarto renders, `scripts/build_colab_notebooks.py` converts eligible pages
to explicit paths under `docs/_site/notebooks/`.

- Do not hand-edit generated notebooks in `docs/_site`.
- Keep every `colab_notebook` path unique and aligned with the public course and
  unit structure.
- Intentional-invalid Python fences become learner-editable code cells; their
  marker is documentation metadata, not part of the Python source.
- OJS quiz JSON does not become a Python code cell.
- If source material imports `fcpython`, hide setup/import cells with
  `#| echo: false` when appropriate.

## Validation workflow

Run focused tests while editing, then complete validation before handoff:

```bash
pytest -q
ruff check src tests
ruff format --check src tests
mypy src
poetry check
makim docs.build
```

For curriculum migrations also:

1. search for every retired title, path, lesson ID, and notebook name;
2. verify catalog, outcome map, course home, unit metadata, and sidebar agree;
3. confirm ordinary Python fences parse and invalid ones have exactly one
   marker;
4. confirm quiz JSON parses, IDs are unique, and answer positions remain
   balanced;
5. confirm Mermaid options are present;
6. confirm every new HTML page and generated Colab notebook exists;
7. inspect at least one desktop and narrow-screen quiz when visual tooling is
   available;
8. run `git diff --check`;
9. remove generated artifacts with `makim clean.tmp`;
10. inspect `git status --short` again.

Known note: Quarto may emit non-fatal `OJS block count mismatch` warnings on
pages with multiple OJS quizzes. Treat the build as successful only when it
finishes and reports the output site.

## CI and publishing

- `.github/workflows/ci.yml` runs lint, tests, package build, and docs build on
  pull requests and pushes to `main`.
- `.github/workflows/docs.yml` renders `docs/_site` and publishes it to
  `gh-pages` on pushes to `main` and manual dispatch.
- `.github/workflows/release.yml` is intentionally disabled/no-op; there is no
  package publishing workflow at present.

## Generated files and cleanup

Do not commit local or generated artifacts, including:

- `docs/_site/`
- `docs/.quarto/`
- `.quarto-tmp/`
- `.cache/`
- pytest, MyPy, and Ruff cache directories
- `build/`, `dist/`, and package metadata directories
- Quarto-generated `_files` directories under course or resource pages

Use `makim clean.tmp` or an equivalent safe cleanup before handoff.
