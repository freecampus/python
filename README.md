# FreeCampus Python

A beginner-first portfolio of connected Python courses for learners ranging from
zero programming experience to advanced, scientific, and machine-learning work.

The portfolio starts with no-install practice in Google Colab, then branches
into software-development, scientific-computing, and statistics pathways.
Lessons remain cohesive, hands-on labs with quizzes, debugging practice, and
generated Colab notebooks.

## Start learning

- Portfolio home: [`docs/index.qmd`](docs/index.qmd)
- Course catalog: [`docs/courses/index.qmd`](docs/courses/index.qmd)
- Pathway guide: [`docs/pathways/index.qmd`](docs/pathways/index.qmd)
- Python Foundations:
  [`docs/courses/python-foundations/index.qmd`](docs/courses/python-foundations/index.qmd)
- First lesson:
  [`docs/courses/python-foundations/milestones/first-programs/units/get-started/meet-python-first-program.qmd`](docs/courses/python-foundations/milestones/first-programs/units/get-started/meet-python-first-program.qmd)
- Google Colab:
  [`docs/courses/python-foundations/milestones/first-programs/units/get-started/notebook-workflows.qmd`](docs/courses/python-foundations/milestones/first-programs/units/get-started/notebook-workflows.qmd)
- Lists lesson:
  [`docs/courses/python-foundations/milestones/work-with-data/units/collections-iteration/lists.qmd`](docs/courses/python-foundations/milestones/work-with-data/units/collections-iteration/lists.qmd)
- Debugging reference:
  [`docs/courses/python-foundations/milestones/reliable-programs/units/errors-exceptions-debugging/failure-categories-tracebacks.qmd`](docs/courses/python-foundations/milestones/reliable-programs/units/errors-exceptions-debugging/failure-categories-tracebacks.qmd)
- Learner profiles:
  [`docs/resources/learner-profiles.qmd`](docs/resources/learner-profiles.qmd)
- Instructor notes:
  [`docs/resources/instructor-notes.qmd`](docs/resources/instructor-notes.qmd)
- Practice immediately in Colab: <https://colab.new>
- Quiz notebook example:
  [`notebooks/03_values_variables_types_quiz.ipynb`](notebooks/03_values_variables_types_quiz.ipynb)

## Course portfolio

1. **Python Foundations**: 97 lessons in 16 units grouped into four milestones,
   with a guided challenge at the end of every unit.
2. **Intermediate Python: Applied Problem Solving**: a challenge-based course
   focused on parsing, modeling, testing, refactoring, and explaining unfamiliar
   problems; curriculum TBD.
3. **Advanced Python: Complex Problem Solving**: a planned course focused on
   multi-stage problems, search, constraints, performance, architecture, and
   trade-offs; curriculum TBD.
4. **Scientific Computing with Python**: NumPy, simulation, Matplotlib, SymPy,
   and SciPy, with a larger applied curriculum in development.
5. **Statistics with Python**: a planned course about probability, sampling,
   uncertainty, inference, regression foundations, and responsible statistical
   conclusions; curriculum TBD.
6. **Data Science and Machine Learning with Python**: pandas, seaborn, model
   training, AI libraries, and responsible AI, with applied pipelines and a
   capstone in development.

Python Foundations is the common entry point. Intermediate leads to Advanced;
Scientific Computing and Statistics are parallel, unordered prerequisites for
Data Science and Machine Learning. The canonical course and unit definitions
live in [`docs/courses/_catalog.yml`](docs/courses/_catalog.yml).

Lessons are cohesive rather than microscopic. A page can contain multiple
section-level OJS quizzes so students review one idea before moving to the next.
Reusable notebook quizzes live in `src/fcpython` and can be rendered with
ipywidgets in Jupyter or Google Colab.

Canonical teaching sources live with their owning course under `docs/courses/`.
Sources and generated notebooks mirror the
`milestones/<milestone-id>/units/<unit-id>/` hierarchy. Cross-course material
such as the FAQ and project toolkit lives under `docs/resources/`.

### Python Foundations progress

Python Foundations curriculum version 22 can be completed independently. It
contains 97 lessons, 16 unit challenges, and four milestone challenges in one
learning sequence. Progress is stored in the learner's browser for convenience.
It is self-reported and is not a verified certificate, identity record, or
instructor grade. A final project and certificate are planned and will be
announced later.

## Local planning note

`PLAN.md` is intentionally ignored by git. It is for local course planning, not
the public roadmap.

## Development

This repository uses Python packaging infrastructure with Poetry, Makim, Ruff,
pytest, and Quarto documentation.

Install development dependencies in your preferred environment, then run:

```bash
makim docs.build
makim tests.linter
makim tests.unit
```

To preview the documentation locally:

```bash
makim docs.preview
```

### Course structure check

CI runs the
[FreeCampus Course Structure Check](https://github.com/freecampus/freecampus-course-check)
on every pull request and push to `main`. The independent `Course structure` job
checks the repository's `docs/` sources with release `0.2.0`, pinned to its full
commit SHA. It reports file-specific errors, suggested fixes, and links to
rule-specific troubleshooting examples in annotations and the job summary; no
Python environment or Quarto installation is needed for this check.

The Quarto project declares `freecampus.schema-version: 1` and
`freecampus.kind: journey`. Every published course has milestones, every
milestone has units and a milestone challenge, and every unit has lessons and a
unit challenge. All those pages appear in the sidebar.

Intermediate Python, Advanced Python, and Statistics are still roadmap entries
without lessons. Their public pages live under `docs/roadmap/` and remain in the
catalog and pathways. They must acquire a complete milestone structure before
teaching content is added under `docs/courses/`; empty placeholder lessons are
not a substitute for a curriculum.

See the action's
[troubleshooting guide](https://github.com/freecampus/freecampus-course-check/blob/main/TROUBLESHOOTING.md)
for explanations and examples. CI treats structural violations as failures.

### Milestones and progress

The journey currently has three courses with teaching content, seven milestones,
19 units, and 112 lessons. Each milestone has an overview and an ungraded
integration challenge. The catalog records milestone membership, unit paths, and
both kinds of challenge; the Foundations outcome map records the same groups.

The migration to curriculum 22 preserves existing lesson and unit-challenge IDs
and browser completion records. The new milestone challenges add work to course
completion. Old last-visited URLs are hidden until a current lesson is visited;
the course's Continue button uses completed activities to find the next step.
Progress stays in this browser on this device and is not a grade.

## Project layout

```text
.
├── docs/
│   ├── index.qmd
│   ├── _quarto.yml
│   ├── courses/             # Course → milestones → units → lessons/challenges
│   ├── roadmap/             # Planned courses with no published lessons
│   ├── pathways/
│   ├── resources/           # Shared FAQ, guidance, and project toolkit
│   ├── _includes/           # Shared OJS and Colab includes
│   └── _templates/          # Authoring templates
├── notebooks/
├── src/fcpython/
└── tests/
```

### Downloadable Foundations book

The documentation publishing job builds a complete A4 study book from the
canonical Foundations QMD files. The Python home page and Foundations overview
link to `downloads/python-foundations.pdf`. The cover PNG and JSON manifest are
generated alongside it; the manifest supplies the displayed page count, file
size, and curriculum version. PDF binaries are build artifacts, not tracked
sources.

Install `scripts/pdf/requirements.txt`, Quarto, `fonts-dejavu-core`, and
`poppler-utils`, then run:

```bash
makim docs.build     # Website, Colab notebooks, and the complete PDF
makim docs.site      # Website and notebooks only, for faster local iteration
makim docs.pdf       # PDF, cover preview, and manifest only
python scripts/verify_course_pdf.py
```

The PDF includes milestone overviews and challenges as well as every unit
overview, lesson, and challenge in catalog order. Its separate front matter
explains offline study and printed code wrapping. Browser quizzes become
printable questions with an answer key; hints and solutions are visible,
diagrams become page-sized vectors, and lesson links return to the website and
Colab. No lesson code executes during the build. PDF reading does not update
browser progress or create a verified credential.

For a quick development preview, use
`--limit-units 1 --output build/pdf/preview.pdf` with
`scripts/build_course_pdf.py`. Never publish a preview as the complete book. The
documentation workflow verifies the complete artifact before publishing and
uploads the book, cover, and manifest for pull-request review.
