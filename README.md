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
  [`docs/lessons/foundations-project/index.qmd`](docs/lessons/foundations-project/index.qmd)
- First lesson:
  [`docs/lessons/getting-started/what-is-programming.qmd`](docs/lessons/getting-started/what-is-programming.qmd)
- Google Colab:
  [`docs/lessons/getting-started/google-colab.qmd`](docs/lessons/getting-started/google-colab.qmd)
- Lists lesson:
  [`docs/lessons/data-structures/lists.qmd`](docs/lessons/data-structures/lists.qmd)
- Debugging reference:
  [`docs/lessons/debugging/error-messages.qmd`](docs/lessons/debugging/error-messages.qmd)
- Learner profiles:
  [`docs/lessons/learner-profiles.qmd`](docs/lessons/learner-profiles.qmd)
- Instructor notes:
  [`docs/lessons/instructor-notes.qmd`](docs/lessons/instructor-notes.qmd)
- Practice immediately in Colab: <https://colab.new>
- Quiz notebook example:
  [`notebooks/03_values_variables_types_quiz.ipynb`](notebooks/03_values_variables_types_quiz.ipynb)

## Course portfolio

1. **Python Foundations**: 18 required lessons, one optional local-tools lesson,
   five practical module checkpoints, and a rubric-scored study-tracker project.
2. **Intermediate Python: Building Reliable Applications**: files, projects,
   environments, code quality, and object-oriented Python.
3. **Advanced Python Engineering**: advanced patterns now, with deeper typing,
   concurrency, performance, and API design planned.
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
│   ├── courses/
│   ├── pathways/
│   └── lessons/
├── notebooks/
├── src/fcpython/
└── tests/
```
