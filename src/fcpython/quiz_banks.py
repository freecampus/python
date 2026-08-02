"""Question banks used by FreeCampus Python lessons and notebooks."""

from __future__ import annotations

from fcpython.questions import MultipleChoiceQuestion, Quiz


def values_variables_types_quiz() -> Quiz:
    """Return the checkpoint quiz for values, variables, and types."""
    return Quiz(
        id="values-variables-types",
        title="Values, variables, and types checkpoint",
        questions=(
            MultipleChoiceQuestion(
                id="quoted-number-type",
                prompt='What is the type of the value "42"?',
                options=("int", "float", "str", "bool"),
                answer_index=2,
                explanation=(
                    'Quotation marks create text, so "42" is a string even '
                    "though it contains digits."
                ),
            ),
            MultipleChoiceQuestion(
                id="integer-type",
                prompt="What is the type of the value 42?",
                options=("str", "int", "bool", "list"),
                answer_index=1,
                explanation="Whole numbers without quotation marks are integers.",
            ),
            MultipleChoiceQuestion(
                id="assignment-meaning",
                prompt="What does this line do: price = 10?",
                options=(
                    "It checks whether price already equals 10.",
                    "It assigns the value 10 to the name price.",
                    "It prints the value 10.",
                    "It creates a text value named price.",
                ),
                answer_index=1,
                explanation=(
                    "In Python, a single equals sign assigns a value to a name. "
                    "Use == when you want to compare two values."
                ),
            ),
            MultipleChoiceQuestion(
                id="string-addition",
                prompt='Why does "2" + "3" produce "23" instead of 5?',
                options=(
                    "Python made a math mistake.",
                    "The plus sign always creates text.",
                    "Both values are strings, so + joins them together.",
                    "Strings cannot use the plus sign.",
                ),
                answer_index=2,
                explanation=(
                    "When both operands are strings, + performs concatenation: "
                    "it joins text together."
                ),
            ),
        ),
    )


def getting_started_checkpoint_quiz() -> Quiz:
    """Return the Python Foundations Getting Started checkpoint."""
    return Quiz(
        id="foundations-getting-started-checkpoint",
        title="Getting Started knowledge check",
        questions=(
            MultipleChoiceQuestion(
                id="interpreter-role",
                prompt="What does the Python interpreter do with a program?",
                options=(
                    "It reads and runs the program's instructions.",
                    "It guesses what the learner intended.",
                    "It turns every line into printed text.",
                    "It only checks spelling in comments.",
                ),
                answer_index=0,
                explanation=(
                    "The interpreter follows Python instructions and reports "
                    "either results or errors."
                ),
            ),
            MultipleChoiceQuestion(
                id="prediction-loop",
                prompt=(
                    "Which practice sequence gives the strongest evidence of learning?"
                ),
                options=(
                    "Run, copy, and immediately continue.",
                    "Predict, run, compare, explain, and modify.",
                    "Read the solution without running it.",
                    "Change many lines before checking the first result.",
                ),
                answer_index=1,
                explanation=(
                    "Prediction and one controlled modification make the "
                    "difference between an expectation and the result visible."
                ),
            ),
            MultipleChoiceQuestion(
                id="notebook-state",
                prompt="Why should a new notebook usually be run from top to bottom?",
                options=(
                    "Earlier cells may create names used by later cells.",
                    "Python requires every notebook to have ten cells.",
                    "Later cells automatically repair earlier errors.",
                    "Cell order only changes text formatting.",
                ),
                answer_index=0,
                explanation=(
                    "Notebook state depends on which cells ran and in what "
                    "order, so a top-to-bottom run checks reproducibility."
                ),
            ),
            MultipleChoiceQuestion(
                id="assignment-output",
                prompt=(
                    "A cell contains only score = 7. What visible output should "
                    "you expect?"
                ),
                options=(
                    "7",
                    "score",
                    "Usually no visible output; the name is assigned.",
                    "A NameError every time.",
                ),
                answer_index=2,
                explanation=(
                    "Assignment stores a value under a name. Use an expression "
                    "or print call when you want to display it."
                ),
            ),
        ),
    )


def core_python_checkpoint_quiz() -> Quiz:
    """Return the Python Foundations Core Python checkpoint."""
    return Quiz(
        id="foundations-core-python-checkpoint",
        title="Core Python knowledge check",
        questions=(
            MultipleChoiceQuestion(
                id="input-type",
                prompt="What type of value does input() return?",
                options=("int", "str", "bool", "float"),
                answer_index=1,
                explanation=(
                    "input() returns text. Convert that text explicitly when a "
                    "program needs a number."
                ),
            ),
            MultipleChoiceQuestion(
                id="condition-choice",
                prompt="When does the else branch of an if statement run?",
                options=(
                    "Before Python checks the condition.",
                    "Only when every preceding condition in the chain is false.",
                    "After every if branch.",
                    "Only inside a loop.",
                ),
                answer_index=1,
                explanation=(
                    "An if/elif/else chain selects one path; else is the "
                    "fallback when earlier conditions are false."
                ),
            ),
            MultipleChoiceQuestion(
                id="loop-trace",
                prompt="How many times does for number in range(3) run its body?",
                options=("2", "3", "4", "It never stops"),
                answer_index=1,
                explanation=(
                    "range(3) produces 0, 1, and 2, so the body runs three times."
                ),
            ),
            MultipleChoiceQuestion(
                id="indentation-role",
                prompt="What does indentation communicate to Python?",
                options=(
                    "Which statements belong to the same code block.",
                    "Which variable is a string.",
                    "Which comments should be printed.",
                    "How fast a loop should run.",
                ),
                answer_index=0,
                explanation=(
                    "Indentation groups statements inside conditionals, loops, "
                    "functions, and other blocks."
                ),
            ),
        ),
    )


def data_structures_checkpoint_quiz() -> Quiz:
    """Return the Python Foundations Data Structures checkpoint."""
    return Quiz(
        id="foundations-data-structures-checkpoint",
        title="Data Structures knowledge check",
        questions=(
            MultipleChoiceQuestion(
                id="container-choice",
                prompt="Which container best maps each student name to one score?",
                options=("list", "tuple", "dictionary", "set"),
                answer_index=2,
                explanation="A dictionary associates each unique key with a value.",
            ),
            MultipleChoiceQuestion(
                id="unique-values",
                prompt="Which container is designed to keep unique values?",
                options=("set", "list", "string", "tuple"),
                answer_index=0,
                explanation="A set stores unique values and supports membership tests.",
            ),
            MultipleChoiceQuestion(
                id="mutation-alias",
                prompt=(
                    "If backup = tasks and tasks is a list, what happens when "
                    "tasks.append('test') runs?"
                ),
                options=(
                    "Only tasks changes.",
                    "Both names show the changed list.",
                    "Python converts both names to tuples.",
                    "The append call always raises an error.",
                ),
                answer_index=1,
                explanation=(
                    "Both names refer to the same mutable list unless an "
                    "independent copy is created."
                ),
            ),
            MultipleChoiceQuestion(
                id="nested-access",
                prompt=(
                    "For student = {'scores': [8, 10]}, which expression returns 10?"
                ),
                options=(
                    "student[10]",
                    "student['scores'][1]",
                    "student.scores.10",
                    "student['scores'][10]",
                ),
                answer_index=1,
                explanation=(
                    "First select the list stored under 'scores', then select "
                    "the value at index 1."
                ),
            ),
        ),
    )


def functions_checkpoint_quiz() -> Quiz:
    """Return the Python Foundations Functions checkpoint."""
    return Quiz(
        id="foundations-functions-checkpoint",
        title="Functions knowledge check",
        questions=(
            MultipleChoiceQuestion(
                id="return-purpose",
                prompt="Why does a function return a value?",
                options=(
                    "So its result can be stored or used by other code.",
                    "So Python prints every local variable.",
                    "So the function can avoid having a name.",
                    "So arguments become comments.",
                ),
                answer_index=0,
                explanation=(
                    "A returned value crosses the function boundary and can be "
                    "assigned, compared, printed, or passed elsewhere."
                ),
            ),
            MultipleChoiceQuestion(
                id="parameter-argument",
                prompt="In greet('Mina'), what is 'Mina'?",
                options=(
                    "A return statement",
                    "An argument",
                    "A function name",
                    "A type hint",
                ),
                answer_index=1,
                explanation="The call supplies the argument 'Mina' to a parameter.",
            ),
            MultipleChoiceQuestion(
                id="contract-purpose",
                prompt="What should a useful function contract explain?",
                options=(
                    "Expected inputs, returned result, and important behavior.",
                    "Only the author's name.",
                    "Every value ever used by the program.",
                    "The color of the editor theme.",
                ),
                answer_index=0,
                explanation=(
                    "A contract helps callers understand how to use the "
                    "function and what result to expect."
                ),
            ),
            MultipleChoiceQuestion(
                id="focused-test",
                prompt="What makes a first function test useful?",
                options=(
                    "It checks one stated behavior with a known input and result.",
                    "It depends on many unrelated functions.",
                    "It prints output without checking it.",
                    "It changes the function while running.",
                ),
                answer_index=0,
                explanation=(
                    "A focused example makes failures easier to understand and "
                    "connect to the function's contract."
                ),
            ),
        ),
    )


def debugging_checkpoint_quiz() -> Quiz:
    """Return the Python Foundations Debugging checkpoint."""
    return Quiz(
        id="foundations-debugging-checkpoint",
        title="Debugging knowledge check",
        questions=(
            MultipleChoiceQuestion(
                id="traceback-first-step",
                prompt="What should you identify first in a Python traceback?",
                options=(
                    "The exception type, message, and relevant line.",
                    "A random line to rewrite.",
                    "The editor's font size.",
                    "A package to reinstall immediately.",
                ),
                answer_index=0,
                explanation=(
                    "The exception type, message, and line provide evidence "
                    "about what Python could not do."
                ),
            ),
            MultipleChoiceQuestion(
                id="inspect-state",
                prompt="Why add a focused print statement or breakpoint?",
                options=(
                    "To inspect a value at the point where behavior changes.",
                    "To make the program permanently longer.",
                    "To hide the original error.",
                    "To replace every test.",
                ),
                answer_index=0,
                explanation=(
                    "Inspecting state tests a specific explanation instead of "
                    "changing code by guesswork."
                ),
            ),
            MultipleChoiceQuestion(
                id="mre-purpose",
                prompt="What does a minimal reproducible example preserve?",
                options=(
                    "The smallest code and data that still show the problem.",
                    "Every feature in the original project.",
                    "Only the expected output.",
                    "A screenshot without executable code.",
                ),
                answer_index=0,
                explanation=(
                    "Removing unrelated parts makes the cause easier to isolate "
                    "while keeping the failure reproducible."
                ),
            ),
            MultipleChoiceQuestion(
                id="controlled-fix",
                prompt="After forming a debugging hypothesis, what should you do next?",
                options=(
                    "Change one relevant thing and rerun the smallest example.",
                    "Rewrite the entire program before running it.",
                    "Ignore the actual output.",
                    "Delete the traceback.",
                ),
                answer_index=0,
                explanation=(
                    "One controlled change lets you compare evidence and decide "
                    "whether the hypothesis was supported."
                ),
            ),
        ),
    )


def python_foundations_checkpoint_quizzes() -> tuple[Quiz, ...]:
    """Return the five required Python Foundations checkpoint quizzes."""
    return (
        getting_started_checkpoint_quiz(),
        core_python_checkpoint_quiz(),
        data_structures_checkpoint_quiz(),
        functions_checkpoint_quiz(),
        debugging_checkpoint_quiz(),
    )


def python_foundations_project_quiz() -> Quiz:
    """Return the readiness quiz for the Python Foundations project."""
    return Quiz(
        id="python-foundations-project-readiness",
        title="Foundations project readiness check",
        questions=(
            MultipleChoiceQuestion(
                id="project-scope",
                prompt="Which project scope best fits Python Foundations?",
                options=(
                    "A small program using course concepts that can be explained "
                    "line by line.",
                    "A production web platform with authentication and payments.",
                    "A project copied from a tutorial without changes.",
                    "A program that depends on unexplained advanced libraries.",
                ),
                answer_index=0,
                explanation=(
                    "A small explainable program provides stronger Foundations "
                    "evidence than a large project built from unfamiliar parts."
                ),
            ),
            MultipleChoiceQuestion(
                id="project-evidence",
                prompt="Which evidence should remain with the finished project?",
                options=(
                    "Only a screenshot of the final output.",
                    "Working code, example runs, checks, explanations, and "
                    "debugging notes.",
                    "Only the original project idea.",
                    "A claim that the program worked once.",
                ),
                answer_index=1,
                explanation=(
                    "Multiple forms of evidence show that the learner can run, "
                    "explain, modify, check, and debug the project."
                ),
            ),
            MultipleChoiceQuestion(
                id="rubric-use",
                prompt=(
                    "What should you do when one required rubric row is still "
                    "'Not yet'?"
                ),
                options=(
                    "Record the project complete anyway.",
                    "Hide that part of the project.",
                    "Revise the project and collect new evidence for that row.",
                    "Add unrelated features instead.",
                ),
                answer_index=2,
                explanation=(
                    "The completion threshold requires evidence for every "
                    "required row, so revise the specific gap before recording."
                ),
            ),
            MultipleChoiceQuestion(
                id="local-recognition",
                prompt="What does the project's browser completion marker prove?",
                options=(
                    "It is a verified academic credential.",
                    "It is a self-reported local record, not independently "
                    "verified evidence.",
                    "It permanently submits the project to an instructor.",
                    "It creates a public certificate ID.",
                ),
                answer_index=1,
                explanation=(
                    "The static site stores local progress for the learner's "
                    "convenience; it does not verify identity or assess evidence."
                ),
            ),
        ),
    )
