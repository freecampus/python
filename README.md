# FreeCampus Python

A beginner-first portfolio of connected Python courses for learners ranging from
zero programming experience to advanced, scientific, and machine-learning work.

The portfolio starts with no-install practice in Google Colab, then branches
into software-development and scientific-data pathways. Lessons remain cohesive,
hands-on labs with quizzes, debugging practice, and generated Colab notebooks.

## Start learning

- Portfolio home: [`docs/index.qmd`](docs/index.qmd)
- Course catalog: [`docs/courses/index.qmd`](docs/courses/index.qmd)
- Pathway guide: [`docs/pathways/index.qmd`](docs/pathways/index.qmd)
- Python Foundations:
  [`docs/courses/python-foundations/index.qmd`](docs/courses/python-foundations/index.qmd)
- Python Foundations project and rubric:
  [`docs/courses/python-foundations/project/index.qmd`](docs/courses/python-foundations/project/index.qmd)
- First lesson:
  [`docs/courses/python-foundations/getting-started/what-is-programming.qmd`](docs/courses/python-foundations/getting-started/what-is-programming.qmd)
- Google Colab:
  [`docs/courses/python-foundations/getting-started/google-colab.qmd`](docs/courses/python-foundations/getting-started/google-colab.qmd)
- Lists lesson:
  [`docs/courses/python-foundations/data-structures/lists.qmd`](docs/courses/python-foundations/data-structures/lists.qmd)
- Debugging reference:
  [`docs/courses/python-foundations/debugging/error-messages.qmd`](docs/courses/python-foundations/debugging/error-messages.qmd)
- Learner profiles:
  [`docs/resources/learner-profiles.qmd`](docs/resources/learner-profiles.qmd)
- Instructor notes:
  [`docs/resources/instructor-notes.qmd`](docs/resources/instructor-notes.qmd)
- Practice immediately in Colab: <https://colab.new>
- Quiz notebook example:
  [`notebooks/03_values_variables_types_quiz.ipynb`](notebooks/03_values_variables_types_quiz.ipynb)

## Course portfolio

1. **Python Foundations**: 18 required lessons, five practical module
   checkpoints, a rubric-scored project, and 20 optional lessons covering local
   tools, files, environments, code quality, OOP, and Python patterns.
2. **Intermediate Python: Applied Problem Solving**: a challenge-based course
   focused on parsing, modeling, testing, refactoring, and explaining unfamiliar
   problems; curriculum TBD.
3. **Advanced Python: Complex Problem Solving**: a planned course focused on
   multi-stage problems, search, constraints, performance, architecture, and
   trade-offs; curriculum TBD.
4. **Scientific Computing with Python**: NumPy, simulation, Matplotlib, SymPy,
   and SciPy, with a larger applied curriculum in development.
5. **Data Science and Machine Learning with Python**: pandas, seaborn, model
   training, AI libraries, and responsible AI, with applied pipelines and a
   capstone in development.

Python Foundations is the common entry point. Intermediate leads to Advanced;
Scientific Computing leads to Data Science and Machine Learning. The canonical
course and module definitions live in
[`docs/courses/_catalog.yml`](docs/courses/_catalog.yml).

Lessons are cohesive rather than microscopic. A page can contain multiple
section-level OJS quizzes so students review one idea before moving to the next.
Reusable notebook quizzes live in `src/fcpython` and can be rendered with
ipywidgets in Jupyter or Google Colab.

Canonical teaching sources live with their owning course under `docs/courses/`.
Cross-course material such as the FAQ and project toolkit lives under
`docs/resources/`. Published `/lessons/...` pages and `notebooks/lessons/...`
Colab URLs remain available as compatibility paths.

### Python Foundations completion

Python Foundations curriculum version 1 can now be completed independently. The
local completion rule requires all 18 required lessons, all five module
checkpoints, and the Foundations project self-assessed against rubric version 1.
Progress is stored in the learner's browser for convenience. It is self-reported
and is not a verified certificate, identity record, or instructor grade.

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

## Project layout

```text
.
├── docs/
│   ├── index.qmd
│   ├── _quarto.yml
│   ├── courses/             # Course homes and course-owned modules
│   ├── pathways/
│   ├── resources/           # Shared FAQ, guidance, and project toolkit
│   ├── _includes/           # Shared OJS and Colab includes
│   └── _templates/          # Authoring templates
├── notebooks/
├── src/fcpython/
└── tests/
```
