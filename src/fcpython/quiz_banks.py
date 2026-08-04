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
            "get-started",
            "Get Started",
            "predict, run, explain, modify, and cleanly rerun a small example",
        ),
        (
            "python-syntax",
            "Learning to Read and Write Python Code",
            "identify expressions, statements, keywords, and blocks before "
            "reasoning about behavior",
        ),
        (
            "core-values-types",
            "Numbers, Text, and Other Values",
            "choose values for counts, measurements, money, text, truth, missing "
            "information, and time while explaining their boundaries",
        ),
        (
            "collections-iteration",
            "Organizing and Traversing Collections",
            "choose, traverse, combine, and sort collections without losing the "
            "relationships between their values",
        ),
        (
            "decisions-repetition",
            "Making Decisions and Repeating Work",
            "build complete decisions and loops that transform, search, and stop "
            "deliberately",
        ),
        (
            "functions-call-behavior",
            "Building Reusable Functions",
            "design, compose, and trace functions with explicit inputs, results, "
            "scope, and reusable behavior",
        ),
        (
            "mutability-identity-copying",
            "Sharing, Changing, and Copying Objects",
            "trace shared objects and choose mutation, ownership, or copying "
            "deliberately",
        ),
        (
            "problem-solving-algorithms",
            "Solving Problems with Algorithms",
            "specify, decompose, select, and defend cooperating algorithms",
        ),
        (
            "errors-exceptions-debugging",
            "Errors, Exceptions, and Debugging",
            "read a failure, handle anticipated exceptions, and test one "
            "evidence-based hypothesis",
        ),
        (
            "files-paths-external-data",
            "Files, Paths, and External Data",
            "cross file, text, binary, and structured-data boundaries explicitly",
        ),
        (
            "modules-environments-projects",
            "Modules, Environments, and Python Projects",
            "organize and clean-install a versioned multi-file project",
        ),
        (
            "object-oriented-python",
            "Object-Oriented Python and Dataclasses",
            "model cohesive state and behavior without unnecessary abstraction",
        ),
        (
            "command-line-applications",
            "Command-Line Applications",
            "separate command parsing, domain behavior, streams, and exit status",
        ),
        (
            "testing-python-programs",
            "Testing Python Programs",
            "choose test boundaries whose failures identify violated behavior",
        ),
        (
            "code-quality-maintainability",
            "Code Quality and Maintainability",
            "improve clarity while preserving behavior with automated checks",
        ),
        (
            "documentation-publishing",
            "Documentation as Part of the Product",
            "build and publish documentation whose examples and links are verified",
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
