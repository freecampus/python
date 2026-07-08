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
- Full course plan: [`PLAN.md`](PLAN.md)
- Practice immediately in Colab: <https://colab.new>

## Course structure

1. **First contact**: mindset, Colab, local setup, VS Code, Jupyter.
2. **Core Python**: values, variables, strings, conditionals, loops, data
   structures, and functions.
3. **Independent Python**: debugging, files, exceptions, modules, packages,
   environments, testing, PEP 8, linting, formatting, and type hints.
4. **Deeper Python**: classes, comprehensions, generators, decorators, and
   context managers.
5. **Applied Python**: scientific libraries, data science libraries,
   introductory AI libraries, and a capstone project.

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
├── PLAN.md
├── docs/
│   ├── index.qmd
│   ├── _quarto.yml
│   └── lessons/
├── src/fcpython/
└── tests/
```
