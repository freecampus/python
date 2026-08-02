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


def core_programming_milestone_quiz() -> Quiz:
    """Return the Core Programming milestone checkpoint."""
    return Quiz(
        id="foundations-core-programming-milestone",
        title="Core Programming knowledge check",
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
        ),
    )


def data_and_functions_milestone_quiz() -> Quiz:
    """Return the Data and Functions milestone checkpoint."""
    return Quiz(
        id="foundations-data-and-functions-milestone",
        title="Data and Functions knowledge check",
        questions=(
            MultipleChoiceQuestion(
                id="container-choice",
                prompt="Which container best maps each student name to one score?",
                options=("list", "tuple", "dictionary", "set"),
                answer_index=2,
                explanation="A dictionary associates each unique key with a value.",
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


def debugging_and_data_boundaries_milestone_quiz() -> Quiz:
    """Return the Debugging and Data Boundaries milestone checkpoint."""
    return Quiz(
        id="foundations-debugging-and-data-boundaries-milestone",
        title="Debugging and Data Boundaries knowledge check",
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
                id="file-context",
                prompt="Why use with open(...) as file for file access?",
                options=(
                    "It closes the file reliably when the block finishes.",
                    "It converts every file to JSON.",
                    "It guarantees every path exists.",
                    "It prevents all validation errors.",
                ),
                answer_index=0,
                explanation=(
                    "The context manager releases the file resource even when "
                    "the block finishes because of an error."
                ),
            ),
            MultipleChoiceQuestion(
                id="validation-boundary",
                prompt="When should external data be validated?",
                options=(
                    "As it enters the program, before other code depends on it.",
                    "Only after every calculation finishes.",
                    "Only when Python raises SyntaxError.",
                    "Never when the source is a file.",
                ),
                answer_index=0,
                explanation=(
                    "Checking data at the boundary creates clear failures before "
                    "invalid values spread through the program."
                ),
            ),
        ),
    )


def reliable_projects_milestone_quiz() -> Quiz:
    """Return the Reliable Projects milestone checkpoint."""
    return Quiz(
        id="foundations-reliable-projects-milestone",
        title="Reliable Python Projects knowledge check",
        questions=(
            MultipleChoiceQuestion(
                id="module-boundary",
                prompt="Why move reusable behavior from a script into a module?",
                options=(
                    "So it can be imported, tested, and reused behind a clear "
                    "boundary.",
                    "So Python stops checking its syntax.",
                    "So every function becomes global.",
                    "So dependencies install automatically.",
                ),
                answer_index=0,
                explanation=(
                    "A focused module gives related behavior a reusable, testable home."
                ),
            ),
            MultipleChoiceQuestion(
                id="environment-purpose",
                prompt="What problem does a project virtual environment solve?",
                options=(
                    "It isolates that project's dependency versions.",
                    "It replaces source control.",
                    "It makes every command-line argument valid.",
                    "It publishes the project automatically.",
                ),
                answer_index=0,
                explanation=(
                    "An isolated environment prevents one project's packages "
                    "from silently changing another project's runtime."
                ),
            ),
            MultipleChoiceQuestion(
                id="test-contract",
                prompt="What should a focused pytest test describe?",
                options=(
                    "One observable behavior and its expected result.",
                    "The editor theme used by the author.",
                    "Every implementation detail in one assertion.",
                    "A result inspected only by printing it.",
                ),
                answer_index=0,
                explanation=(
                    "A focused test protects one behavior and makes a failure "
                    "easier to interpret."
                ),
            ),
            MultipleChoiceQuestion(
                id="automation-role",
                prompt="What do pre-commit checks and CI provide together?",
                options=(
                    "Repeatable quality checks before and after changes are shared.",
                    "A guarantee that no program can contain a bug.",
                    "A replacement for tests and code review.",
                    "Automatic type conversion at runtime.",
                ),
                answer_index=0,
                explanation=(
                    "Local and remote automation run the same agreed checks at "
                    "important points in the project workflow."
                ),
            ),
        ),
    )


def abstractions_and_application_patterns_milestone_quiz() -> Quiz:
    """Return the Abstractions and Application Patterns milestone checkpoint."""
    return Quiz(
        id="foundations-abstractions-and-application-patterns-milestone",
        title="Abstractions and Application Patterns knowledge check",
        questions=(
            MultipleChoiceQuestion(
                id="class-purpose",
                prompt="When is a small class a useful design choice?",
                options=(
                    "When related state and behavior form one clear concept.",
                    "Whenever a program has one variable.",
                    "Only when inheritance is required.",
                    "When functions should become impossible to test.",
                ),
                answer_index=0,
                explanation=(
                    "A class can make a cohesive concept explicit by keeping its "
                    "state and operations together."
                ),
            ),
            MultipleChoiceQuestion(
                id="dataclass-purpose",
                prompt="What does @dataclass mainly reduce for data-focused classes?",
                options=(
                    "Repetitive methods such as initialization and representation.",
                    "The need to choose meaningful attributes.",
                    "All runtime validation.",
                    "The need to create instances.",
                ),
                answer_index=0,
                explanation=(
                    "A dataclass generates common methods while leaving the data "
                    "model and behavior visible."
                ),
            ),
            MultipleChoiceQuestion(
                id="generator-value",
                prompt="Why can a generator help with a long sequence of values?",
                options=(
                    "It produces values on demand instead of storing them all at once.",
                    "It automatically sorts every value.",
                    "It converts every value to text.",
                    "It prevents iteration from stopping.",
                ),
                answer_index=0,
                explanation=(
                    "Lazy generation can reduce memory use and lets a pipeline "
                    "process one value at a time."
                ),
            ),
            MultipleChoiceQuestion(
                id="context-boundary",
                prompt="What behavior should a context manager make explicit?",
                options=(
                    "Setup and guaranteed cleanup around a block of work.",
                    "A hidden global variable shared by every module.",
                    "An infinite loop around a function.",
                    "Automatic inheritance between unrelated classes.",
                ),
                answer_index=0,
                explanation=(
                    "A context manager pairs resource setup with reliable cleanup "
                    "at a visible block boundary."
                ),
            ),
        ),
    )


def python_foundations_milestone_checkpoint_quizzes() -> tuple[Quiz, ...]:
    """Return the five required Python Foundations milestone quizzes."""
    return (
        core_programming_milestone_quiz(),
        data_and_functions_milestone_quiz(),
        debugging_and_data_boundaries_milestone_quiz(),
        reliable_projects_milestone_quiz(),
        abstractions_and_application_patterns_milestone_quiz(),
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
