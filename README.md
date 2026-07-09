# FreeCampus Python

A beginner-first Python course for learners with low or zero programming
experience.

The course starts with no-install practice in Google Colab, then gradually moves
through local Python, VS Code, Jupyter, core programming concepts, debugging,
testing, style, scientific Python, data science, introductory AI libraries, and
a capstone portfolio project.

## Start learning

- Course home: [`docs/index.qmd`](docs/index.qmd)
- Lesson path: [`docs/lessons/index.qmd`](docs/lessons/index.qmd)
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

## Course structure

1. **Getting Started**: mindset, Colab, local Python tools.
2. **Core Python**: values/variables/types, strings/input/output, conditionals,
   loops/tracing.
3. **Data Structures**: lists, tuples, dictionaries, sets, and nested data as
   cohesive lessons.
4. **Functions**: basics, contracts, decomposition, and testing.
5. **Debugging and data I/O**: error messages, debugging tools, files,
   structured data, exceptions, and validation.
6. **Projects and quality**: modules/packages, environments/dependencies,
   command-line programs, layout, tests, style, Ruff, mypy, and CI.
7. **Deeper Python**: OOP, dataclasses, design, comprehensions,
   iteration/generators, decorators, context managers, logging, and
   configuration.
8. **Applied Python**: NumPy, Matplotlib, SymPy, SciPy, pandas, seaborn,
   scikit-learn, PyTorch, TensorFlow/Keras, Transformers, responsible AI, and a
   capstone.

Lessons are cohesive rather than microscopic. A page can contain multiple
section-level OJS quizzes so students review one idea before moving to the next.
Reusable notebook quizzes live in `src/fcpython` and can be rendered with
ipywidgets in Jupyter or Google Colab.

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
│   └── lessons/
├── notebooks/
├── src/fcpython/
└── tests/
```
