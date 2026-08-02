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


QuestionSpec = tuple[str, str, tuple[str, ...], int, str]
ChallengeQuizSpec = tuple[str, str, tuple[QuestionSpec, ...]]


def _quiz_from_spec(spec: ChallengeQuizSpec) -> Quiz:
    quiz_id, title, questions = spec
    return Quiz(
        id=quiz_id,
        title=title,
        questions=tuple(
            MultipleChoiceQuestion(
                id=question_id,
                prompt=prompt,
                options=options,
                answer_index=answer_index,
                explanation=explanation,
            )
            for question_id, prompt, options, answer_index, explanation in questions
        ),
    )


def python_foundations_unit_challenge_quizzes() -> tuple[Quiz, ...]:
    """Return one orientation quiz for each current Foundations challenge.

    Challenge pages contain the full task-specific assessment. This bank keeps a
    reusable, lightweight orientation check for widget-based notebooks.
    """
    units = (
        (
            "learning-workflow-tools",
            "Learning Workflow and Tools",
            "predict, run, explain, change, and cleanly rerun a small example",
        ),
        (
            "numeric-foundations",
            "Values, Names, and Numeric Computation",
            "trace numeric values and justify the operation and rounding rule",
        ),
        (
            "text-input-output",
            "Text, Unicode, Input, and Output",
            "preserve text while distinguishing characters, code points, "
            "and encoded bytes",
        ),
        (
            "decisions",
            "Boolean Logic and Decisions",
            "translate a rule table into branches with verified boundaries",
        ),
        (
            "loops-and-state",
            "Loops, Tracing, and State",
            "show how loop state progresses toward a stopping condition",
        ),
        (
            "problem-solving-algorithms",
            "Problem Decomposition and Basic Algorithms",
            "derive a small algorithm from acceptance examples and pseudocode",
        ),
        (
            "sequences",
            "Sequences: Lists and Tuples",
            "preserve order while choosing deliberate mutable and immutable "
            "representations",
        ),
        (
            "mappings-and-sets",
            "Mappings, Sets, and Nested Data",
            "model lookup, uniqueness, counting, and nested records with "
            "suitable containers",
        ),
        (
            "mutability-and-copying",
            "Mutability, Identity, and Copying",
            "explain and repair an accidental shared-state mutation",
        ),
        (
            "functions-and-interfaces",
            "Functions and Interfaces",
            "implement a focused function contract with independent checks",
        ),
        (
            "scope-and-call-stacks",
            "Scope, Call Stacks, and Functions as Values",
            "trace call-local state and returned values through nested calls",
        ),
        (
            "debugging",
            "Debugging and Reproducible Failures",
            "reduce a failure and test one evidence-based hypothesis",
        ),
        (
            "files-and-paths",
            "Files, Paths, and Encodings",
            "perform an idempotent UTF-8 file transformation with portable paths",
        ),
        (
            "structured-data-and-patterns",
            "Structured Data and Text Patterns",
            "parse, validate, transform, and report structured input in stages",
        ),
        (
            "exceptions-and-validation",
            "Exceptions and Defensive Programming",
            "reject invalid input and handle only anticipated failures",
        ),
        (
            "modules-and-standard-library",
            "Modules, Imports, and Standard Library",
            "organize importable code and justify a standard-library choice",
        ),
        (
            "reproducible-projects",
            "Reproducible Python Projects",
            "recreate an isolated project from its declared configuration",
        ),
        (
            "git-and-collaboration",
            "Git and Collaboration",
            "produce a clean, reviewable history of focused commits",
        ),
        (
            "command-line-applications",
            "Command-Line Applications",
            "separate command parsing, domain behavior, output streams, and "
            "exit status",
        ),
        (
            "testing-with-pytest",
            "Testing with pytest",
            "write tests whose failures identify a violated behavior boundary",
        ),
        (
            "maintainable-code",
            "Documentation, Style, Linting, and Typing",
            "improve clarity while preserving behavior with automated checks",
        ),
        (
            "object-oriented-python",
            "Object-Oriented Python and Dataclasses",
            "model cohesive state and behavior without unnecessary abstraction",
        ),
        (
            "pythonic-iteration",
            "Pythonic Iteration and Resource Control",
            "select eager or lazy iteration and make resource lifetime explicit",
        ),
        (
            "reliable-project-operations",
            "Operating a Reliable Project",
            "run one documented quality workflow with useful operational evidence",
        ),
    )
    quizzes = []
    for index, (unit_id, title, evidence) in enumerate(units):
        evidence_options = [
            evidence.capitalize() + ".",
            "Copy a working artifact without explaining or rerunning it.",
            "Change several causes before collecting any failure evidence.",
            "Memorize tool names without applying them to observable behavior.",
        ]
        answer_index = index % len(evidence_options)
        evidence_options[0], evidence_options[answer_index] = (
            evidence_options[answer_index],
            evidence_options[0],
        )
        quizzes.append(
            Quiz(
                id=f"foundations-{unit_id}-challenge",
                title=f"{title} challenge orientation",
                questions=(
                    MultipleChoiceQuestion(
                        id="evidence",
                        prompt="Which result is useful evidence for this unit?",
                        options=tuple(evidence_options),
                        answer_index=answer_index,
                        explanation=("The challenge asks you to " + evidence + "."),
                    ),
                    MultipleChoiceQuestion(
                        id="clean-rerun",
                        prompt=(
                            "Why run the complete solution from a clean state before "
                            "recording progress?"
                        ),
                        options=(
                            "To verify that visible code and declared inputs "
                            "reproduce the result.",
                            "To make every algorithm constant time.",
                            "To remove the need for boundary checks.",
                            "To convert every exception into a passing result.",
                        ),
                        answer_index=0,
                        explanation=(
                            "A clean rerun exposes hidden state and missing "
                            "setup steps."
                        ),
                    ),
                ),
            )
        )
    return tuple(quizzes)
