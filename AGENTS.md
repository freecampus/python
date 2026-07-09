# AGENTS.md

Guidance for AI agents and maintainers working in this repository.

## Repository purpose

FreeCampus Python is a beginner-first Python course for learners with low or
zero programming experience. The course is a Quarto website with supporting
Python helpers for reusable quizzes and notebook widgets.

The teaching goal is **zero to practical project confidence**: students should
predict, run, explain, modify, quiz, and debug small examples before moving on.

## Local-first workflow

- Prefer inspecting the local workspace over any remote repository fallback.
- Do not browse or rely on the remote GitHub tree when the local workspace is
  available.
- For non-trivial changes, describe a short implementation plan before editing
  unless the user explicitly asks for direct implementation.
- Protect existing user work. Check `git status --short` before and after edits.
- `PLAN.md` is intentionally ignored by git and is local planning material, not
  the public roadmap.

## Project layout

```text
.
├── docs/                    # Quarto website
│   ├── index.qmd            # Course home
│   ├── _quarto.yml          # Site navigation/config
│   ├── styles.css           # Course callouts, quizzes, diagram styling
│   └── lessons/             # Course chapters and lessons
├── notebooks/               # Jupyter/Colab examples
├── src/fcpython/            # Reusable quiz and widget helpers
├── tests/                   # pytest tests for helpers and docs structure
├── .github/workflows/       # CI and documentation publishing
├── .makim.yaml              # Local task runner commands
└── pyproject.toml           # Package/tool configuration
```

## Course design rules

- Keep lessons **cohesive, not microscopic**. A topic like lists should be one
  rich page with sections, not four tiny pages.
- Multiple OJS quizzes inside one lesson are encouraged when the page has
  multiple sections. Use them as checkpoints before the next section.
- Every public lesson/chapter/support page should include an OJS quiz config and
  the shared OJS include.
- Content lesson pages should start with a compact `.lesson-meta` block that
  states level, estimated time, learning outcome, and practice environment.
- Lesson front matter should include `categories` and `order` so pages can later
  be used by Quarto listings without rebuilding the course map by hand.
- Prefer analogies, small examples, debugging corners, hidden solution paths,
  and references over long abstract explanations.
- Prefer Quarto callouts for standard teaching boxes, such as key ideas,
  analogies, practice prompts, common mistakes, and key points. Keep custom
  classes only for course-specific components such as OJS quiz wrappers and
  concept diagrams.
- Do not use generic "Mental model", "Tiny example", or vague "Walkthrough"
  sections. Prefer concrete headings such as "The problem this lesson solves",
  "First example", "Step-by-step explanation", "Common mistake", and "Check your
  understanding".
- Explain examples line by line for a learner with zero programming experience:
  say what value/name/action appears, what Python does, what changes, and what
  output or error to expect.
- Use clean numbered lesson sections such as `## 1. Strings are text values`,
  not generated-sounding headings such as `## Section 1: Strings`.
- Use Mermaid diagrams selectively for concepts that need a visual explanation
  such as variables, conditionals, loops, functions, lists, dictionaries,
  tracebacks, environments, OOP, decorators, and ML workflows.
- Keep examples beginner-safe: one idea at a time, explicit prediction prompts,
  and small modifications.

## Quarto and lesson conventions

- Site config lives in `docs/_quarto.yml`; update sidebar navigation whenever
  adding, removing, or renaming lesson pages.
- Shared OJS renderer: `docs/lessons/_includes/ojs-quiz.qmd`.
- For root lesson pages, include with:

  ```markdown
  {{< include _includes/ojs-quiz.qmd >}}
  ```

- For chapter lesson pages one directory below `docs/lessons`, include with:

  ```markdown
  {{< include ../_includes/ojs-quiz.qmd >}}
  ```

- Quarto execution is disabled globally with `execute.eval: false`. Avoid adding
  executable Python chunks that require a kernel during docs builds.
- If a notebook or example imports from `fcpython`, keep setup/import cells
  hidden in rendered teaching material with `#| echo: false` when appropriate.
- Mermaid diagrams should use fenced blocks like:

  ````markdown
  ::: {.concept-diagram} Short explanation of what the diagram illustrates.

  ```{mermaid}
  %%| echo: false
  %%| eval: true
  flowchart LR
    A[Input] --> B[Process] --> C[Output]
  ```

  :::
  ````

  The `%%|` options are required because Quarto execution is disabled globally;
  without them, diagrams render as visible flowchart source code instead of
  browser-rendered Mermaid diagrams.

## Quiz/widget helpers

- Reusable quiz data belongs in `src/fcpython/quiz_banks.py`.
- Quiz model classes live in `src/fcpython/questions.py`.
- ipywidgets rendering lives in `src/fcpython/widgets.py`.
- Browser-side lesson quizzes use static JSON in
  `<script type="application/json" class="fcpython-ojs-quiz-config">` blocks
  plus the shared OJS include.
- Tests in `tests/test_questions.py` verify quiz JSON, OJS presence, and
  selected Mermaid diagrams.

## Development commands

Common checks:

```bash
pytest -q
ruff check src tests
ruff format --check src tests
mypy src
poetry check
makim docs.build
```

Useful Makim tasks:

```bash
makim docs.build     # Render Quarto site into docs/_site
makim docs.preview   # Build then preview the site
makim tests.unit     # Run pytest
makim tests.linter   # Run pre-commit on all files
makim clean.tmp      # Remove temporary/build artifacts
```

`makim docs.build` sets local `HOME`, `TMPDIR`, `XDG_CACHE_HOME`, and `DENO_DIR`
under the repository to avoid writing into a read-only home/cache environment.

Known note: Quarto may print `OJS block count mismatch` warnings for pages with
OJS quizzes. This warning is currently non-fatal if the site build completes.

## CI and publishing

- `.github/workflows/ci.yml` runs lint, tests, package build, and docs build on
  pull requests and pushes to `main`.
- `.github/workflows/docs.yml` renders the Quarto site and publishes
  `docs/_site` to the `gh-pages` branch on pushes to `main` and manual dispatch.
- `.github/workflows/release.yml` is intentionally disabled/no-op because there
  is no package publishing workflow for now.

## Generated files and cleanup

Do not commit generated or local artifacts such as:

- `docs/_site/`
- `docs/.quarto/`
- `.quarto-tmp/`
- `.cache/`
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `build/`, `dist/`, `*.egg-info/`
- `docs/lessons/**/*_files/`

Use `makim clean.tmp` or an equivalent safe cleanup before handing off work.
