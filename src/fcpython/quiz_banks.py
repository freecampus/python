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
    """Return the required quiz for each Python Foundations unit challenge."""
    specs: tuple[ChallengeQuizSpec, ...] = (
        (
            "foundations-getting-started-challenge",
            "Learning Workflow Readiness Check",
            (
                (
                    "predict-first",
                    (
                        "A code cell prints a value you did not expect. What should "
                        "you do first?"
                    ),
                    (
                        "Replace several lines until the output changes.",
                        (
                            "Write down the output you expected and trace the current "
                            "values."
                        ),
                        "Restart the course from the beginning.",
                        "Ignore the result if the cell ran without an error.",
                    ),
                    1,
                    (
                        "A written prediction gives you something precise to compare "
                        "with the evidence from the run."
                    ),
                ),
                (
                    "controlled-change",
                    "Which experiment is a controlled change?",
                    (
                        "Rename every variable and change all input values at once.",
                        "Copy a different program and compare screenshots.",
                        (
                            "Change one input value, predict the result, and rerun "
                            "the same code."
                        ),
                        "Keep editing without rerunning.",
                    ),
                    2,
                    (
                        "Changing one thing preserves a clear connection between the "
                        "change and the new evidence."
                    ),
                ),
                (
                    "colab-order",
                    (
                        "A Colab cell uses a name created in an earlier cell, but the "
                        "name is undefined. What is the best first check?"
                    ),
                    (
                        "Whether the earlier cell has run in the current session.",
                        "Whether the notebook title contains Python.",
                        "Whether the browser window is maximized.",
                        "Whether every cell has exactly the same length.",
                    ),
                    0,
                    (
                        "Notebook state depends on which cells ran and in what order; "
                        "rerunning from the top exposes hidden state."
                    ),
                ),
                (
                    "clean-rerun",
                    (
                        "Why restart the runtime and run all cells before calling "
                        "notebook work reproducible?"
                    ),
                    (
                        "It makes every program faster.",
                        (
                            "It proves the result does not depend on forgotten hidden "
                            "state."
                        ),
                        "It automatically fixes syntax errors.",
                        "It installs every possible package.",
                    ),
                    1,
                    (
                        "A clean rerun checks that the visible notebook contains "
                        "every step needed to reproduce the result."
                    ),
                ),
                (
                    "choose-colab",
                    (
                        "When is Colab the most useful starting environment for this "
                        "course?"
                    ),
                    (
                        (
                            "When you want to begin in a browser without installing "
                            "Python locally."
                        ),
                        "When you must test a local command-line package layout.",
                        "When you need to inspect a local virtual environment.",
                        (
                            "When the program must run without a web browser or "
                            "internet access."
                        ),
                    ),
                    0,
                    (
                        "Colab removes the initial installation barrier and is "
                        "suitable for the course's early notebook exercises."
                    ),
                ),
                (
                    "choose-local",
                    (
                        "Which task is a strong reason to use local Python tools "
                        "later in the course?"
                    ),
                    (
                        "Selecting an answer in a browser quiz.",
                        "Reading a short code example.",
                        (
                            "Practising project folders, virtual environments, and "
                            "command-line programs."
                        ),
                        "Changing one number in an isolated expression.",
                    ),
                    2,
                    (
                        "Project layout, environments, and CLI work depend on "
                        "filesystem and terminal behavior that local tools expose "
                        "directly."
                    ),
                ),
                (
                    "read-error",
                    (
                        "Python shows a traceback. Which information should you "
                        "identify before editing code?"
                    ),
                    (
                        "Only the color of the error output.",
                        "The exception type, message, and relevant line.",
                        "A package to reinstall immediately.",
                        "Every comment in the program.",
                    ),
                    1,
                    (
                        "The exception type, message, and line are evidence about "
                        "what Python could not do."
                    ),
                ),
                (
                    "explain-copy",
                    (
                        "A copied example works. What turns it into useful learning "
                        "evidence?"
                    ),
                    (
                        "Keeping it unchanged so it always matches the source.",
                        "Running it many times without reading it.",
                        (
                            "Explaining the important lines and predicting a small "
                            "modification."
                        ),
                        "Removing every variable name.",
                    ),
                    2,
                    (
                        "Explanation and controlled modification show that you "
                        "understand the behavior rather than only reproducing it."
                    ),
                ),
                (
                    "input-output",
                    (
                        "A program asks for a name and then displays a greeting. "
                        "Which statement is correct?"
                    ),
                    (
                        "The typed name is input and the displayed greeting is output.",
                        "Both values are comments.",
                        "The greeting is input because Python created it.",
                        "The typed name is an error message.",
                    ),
                    0,
                    (
                        "Input enters the program; output is information the program "
                        "presents after processing."
                    ),
                ),
                (
                    "stuck-routine",
                    (
                        "You are stuck after two guesses. Which next step best "
                        "follows the course method?"
                    ),
                    (
                        "Make several more guesses quickly.",
                        "Delete the failing example.",
                        (
                            "Reduce the problem, inspect one value, and make one "
                            "evidence-based change."
                        ),
                        "Assume the tool is broken.",
                    ),
                    2,
                    (
                        "A smaller reproduction and one inspected value create "
                        "evidence that can confirm or reject a hypothesis."
                    ),
                ),
            ),
        ),
        (
            "foundations-values-types-input-output-challenge",
            "Purchase Summary readiness check",
            (
                (
                    "input-type",
                    "What type does input() return before explicit conversion?",
                    ("int", "str", "float", "bool"),
                    1,
                    "input() returns text, even when the learner types digits.",
                ),
                (
                    "formatted-total",
                    "Which value should be numeric before formatting a money total?",
                    (
                        "The prompt text",
                        "The subtotal",
                        "The item label",
                        "The newline",
                    ),
                    1,
                    (
                        "Arithmetic must produce a numeric subtotal before an "
                        "f-string formats it as money."
                    ),
                ),
            ),
        ),
        (
            "foundations-control-flow-challenge",
            "Savings Goal readiness check",
            (
                (
                    "loop-stop",
                    "What prevents a savings loop from running forever?",
                    (
                        "A balance that changes toward a clear stopping condition.",
                        "A longer variable name.",
                        "Printing the balance twice.",
                        "Converting the target to text.",
                    ),
                    0,
                    (
                        "Each iteration must make progress toward a condition that "
                        "eventually becomes false."
                    ),
                ),
                (
                    "boundary-trace",
                    (
                        "If the starting balance already equals the target, how many "
                        "deposits should a while balance < target loop make?"
                    ),
                    ("One", "Two", "Zero", "It never stops"),
                    2,
                    (
                        "The condition is false before the first iteration, so the "
                        "loop body does not run."
                    ),
                ),
            ),
        ),
        (
            "foundations-data-structures-challenge",
            "Classroom Inventory readiness check",
            (
                (
                    "lookup-shape",
                    "Which structure directly maps each item ID to its record?",
                    ("A dictionary", "A set", "A single string", "A Boolean"),
                    0,
                    "A dictionary associates each unique key with its record.",
                ),
                (
                    "unique-borrowers",
                    "Which structure naturally removes repeated borrower names?",
                    ("A list", "A set", "A tuple containing duplicates", "A float"),
                    1,
                    "A set represents unique values without duplicate entries.",
                ),
            ),
        ),
        (
            "foundations-functions-challenge",
            "Study-Session Report readiness check",
            (
                (
                    "return-boundary",
                    (
                        "Why should total_minutes return a number instead of only "
                        "printing it?"
                    ),
                    (
                        "So callers can store, compare, test, or format the result.",
                        "So the function has no inputs.",
                        "So Python skips the calculation.",
                        "So local variables become global.",
                    ),
                    0,
                    (
                        "A return value crosses the function boundary and remains "
                        "useful to other code."
                    ),
                ),
                (
                    "focused-contract",
                    "What makes a function contract focused?",
                    (
                        "It promises one clear behavior for stated inputs and results.",
                        "It performs every program task at once.",
                        "It depends on hidden global state.",
                        "It changes whenever it is called.",
                    ),
                    0,
                    (
                        "A focused contract makes the behavior explainable and "
                        "independently checkable."
                    ),
                ),
            ),
        ),
        (
            "foundations-debugging-challenge",
            "Bug Clinic readiness check",
            (
                (
                    "first-evidence",
                    "What belongs in a useful first bug report?",
                    (
                        "The observed result, expected result, and reproducible input.",
                        "Only a guess about the fix.",
                        "A screenshot without code or data.",
                        "Every unrelated project file.",
                    ),
                    0,
                    (
                        "A reproducible input and a precise expectation let you "
                        "investigate the same failure repeatedly."
                    ),
                ),
                (
                    "small-change",
                    "Why rerun assertions after one repair?",
                    (
                        (
                            "To verify the change fixed the target behavior without "
                            "hiding another failure."
                        ),
                        "To make the source file longer.",
                        "To avoid reading the failure message.",
                        "To rename every variable.",
                    ),
                    0,
                    "A controlled rerun connects the repair to observable evidence.",
                ),
            ),
        ),
        (
            "foundations-files-challenge",
            "Reading Log readiness check",
            (
                (
                    "path-purpose",
                    "Why pass input and output paths into file functions?",
                    (
                        "It makes the file boundary explicit and easier to test.",
                        "It guarantees every file contains JSON.",
                        "It prevents all operating-system errors.",
                        "It turns paths into numbers.",
                    ),
                    0,
                    (
                        "Explicit paths let checks use temporary files instead of "
                        "hidden working-directory assumptions."
                    ),
                ),
                (
                    "with-file",
                    "What does a with block provide for an opened file?",
                    (
                        "Reliable closing when the block ends.",
                        "Automatic data validation.",
                        "A permanent global variable.",
                        "A guarantee that the path exists.",
                    ),
                    0,
                    (
                        "The context manager closes the file even when work leaves "
                        "the block because of an error."
                    ),
                ),
            ),
        ),
        (
            "foundations-error-handling-and-validation-challenge",
            "Safe Record Import readiness check",
            (
                (
                    "validate-boundary",
                    "When should a record from an external file be validated?",
                    (
                        "As it enters the program, before calculations depend on it.",
                        "Only after every result is printed.",
                        "Only if the file name is long.",
                        "Never when JSON parsing succeeds.",
                    ),
                    0,
                    (
                        "Valid JSON can still contain missing or invalid application "
                        "values, so validate at the boundary."
                    ),
                ),
                (
                    "narrow-except",
                    (
                        "Why catch a specific expected exception rather than "
                        "Exception everywhere?"
                    ),
                    (
                        (
                            "It avoids hiding failures the program does not know how "
                            "to handle."
                        ),
                        "It makes every invalid record valid.",
                        "It removes the need for error messages.",
                        "It prevents syntax errors before running.",
                    ),
                    0,
                    (
                        "A narrow handler documents the failure the program "
                        "understands and lets unexpected defects remain visible."
                    ),
                ),
            ),
        ),
        (
            "foundations-modules-and-packages-challenge",
            "Conversion Package readiness check",
            (
                (
                    "import-boundary",
                    "Why place conversion behavior in an importable module?",
                    (
                        (
                            "It gives reusable behavior a named boundary that other "
                            "code can call."
                        ),
                        "It stops Python from checking syntax.",
                        "It installs dependencies automatically.",
                        "It makes every name global.",
                    ),
                    0,
                    "A module gives related reusable behavior one importable home.",
                ),
                (
                    "module-shadow",
                    (
                        "A local file named statistics.py breaks import statistics. "
                        "What should you inspect first?"
                    ),
                    (
                        "Whether the local filename shadows the intended module.",
                        "The monitor brightness.",
                        "The number of comments.",
                        "Whether every function prints a value.",
                    ),
                    0,
                    (
                        "Python's import search can find a local file before the "
                        "intended module."
                    ),
                ),
            ),
        ),
        (
            "foundations-project-structure-challenge",
            "Task Tracker Structure readiness check",
            (
                (
                    "source-home",
                    (
                        "Where should reusable task-tracker behavior live in the "
                        "target layout?"
                    ),
                    (
                        (
                            "Inside the source package rather than the README or "
                            "generated output."
                        ),
                        "Only inside a screenshot.",
                        "Inside the dependency cache.",
                        "In every test file as a copy.",
                    ),
                    0,
                    "The source package is the clear home for application behavior.",
                ),
                (
                    "separate-entry",
                    "Why keep the entry point thin?",
                    (
                        (
                            "So argument/input handling delegates to reusable "
                            "behavior that can be checked separately."
                        ),
                        "So no functions can be imported.",
                        "So all state becomes global.",
                        "So documentation executes automatically.",
                    ),
                    0,
                    (
                        "A thin entry point separates interface concerns from "
                        "reusable application logic."
                    ),
                ),
            ),
        ),
        (
            "foundations-environments-and-dependencies-challenge",
            "Reproducible Text Tool readiness check",
            (
                (
                    "venv-purpose",
                    "What does a project virtual environment isolate?",
                    (
                        (
                            "That project's interpreter context and installed package "
                            "versions."
                        ),
                        "The project's Git history.",
                        "Every file on the computer.",
                        "Only comments in Python files.",
                    ),
                    0,
                    (
                        "An environment keeps one project's dependencies from "
                        "silently changing another project."
                    ),
                ),
                (
                    "declare-dependency",
                    "Why record a dependency in project metadata after installing it?",
                    (
                        "So another clean environment can reproduce the requirement.",
                        "So Python no longer imports it.",
                        "So the package becomes standard-library code.",
                        "So tests are unnecessary.",
                    ),
                    0,
                    (
                        "A declaration turns local installation state into a "
                        "reproducible project requirement."
                    ),
                ),
            ),
        ),
        (
            "foundations-command-line-programs-challenge",
            "Converter CLI readiness check",
            (
                (
                    "argv-test",
                    "Why let main accept argv=None?",
                    (
                        (
                            "Tests can pass a known argument list while normal runs "
                            "use command-line arguments."
                        ),
                        "It prevents argparse from validating input.",
                        "It converts all arguments to numbers.",
                        "It removes the need for a parser.",
                    ),
                    0,
                    (
                        "An injectable argument list makes parsing behavior "
                        "reproducible in checks."
                    ),
                ),
                (
                    "logic-separation",
                    "Where should the numeric conversion calculation live?",
                    (
                        "In a reusable function separate from printing and parsing.",
                        "Only in the help text.",
                        "Inside every assertion as copied code.",
                        "In a global exception handler.",
                    ),
                    0,
                    (
                        "Separating calculation from the interface makes both easier "
                        "to explain and test."
                    ),
                ),
            ),
        ),
        (
            "foundations-testing-challenge",
            "Grade Summary readiness check",
            (
                (
                    "behavior-test",
                    "What should a focused test protect?",
                    (
                        (
                            "One observable behavior with a known input and expected "
                            "result."
                        ),
                        "The exact order of unrelated implementation lines.",
                        "A printed value that nobody checks.",
                        "The editor theme.",
                    ),
                    0,
                    (
                        "A focused behavior makes failure meaning clear and supports "
                        "safe refactoring."
                    ),
                ),
                (
                    "bug-regression",
                    (
                        "What should you do after finding and repairing a "
                        "boundary-case bug?"
                    ),
                    (
                        "Add a test that reproduces the old failure and now passes.",
                        "Delete the boundary input.",
                        "Replace all tests with one screenshot.",
                        "Test only the happy path again.",
                    ),
                    0,
                    "A regression test preserves the evidence that exposed the bug.",
                ),
            ),
        ),
        (
            "foundations-code-style-and-linting-challenge",
            "Messy Report Rescue readiness check",
            (
                (
                    "format-vs-behavior",
                    "What must remain true after formatting and renaming a script?",
                    (
                        "Its checked observable behavior remains unchanged.",
                        "Every line becomes the same length.",
                        "All functions are removed.",
                        "The script prints more output.",
                    ),
                    0,
                    (
                        "Style improvements should not silently change the behavior "
                        "protected by assertions."
                    ),
                ),
                (
                    "linter-evidence",
                    "What does a clean linter run demonstrate?",
                    (
                        (
                            "The configured static checks found no remaining reported "
                            "issues."
                        ),
                        "The program has no possible bugs.",
                        "Every design choice is ideal.",
                        "Runtime tests are no longer useful.",
                    ),
                    0,
                    (
                        "Linting is one form of evidence, not a proof of complete "
                        "correctness."
                    ),
                ),
            ),
        ),
        (
            "foundations-typing-challenge",
            "Typed Record Summarizer readiness check",
            (
                (
                    "useful-type",
                    "What makes a type annotation useful?",
                    (
                        "It communicates an actual value expectation at a boundary.",
                        "It replaces runtime validation of external data.",
                        "It guarantees the implementation is correct.",
                        "It makes every value a string.",
                    ),
                    0,
                    (
                        "Annotations document expectations and enable static checks, "
                        "but external values still need validation."
                    ),
                ),
                (
                    "avoid-any",
                    "Why avoid replacing every difficult annotation with Any?",
                    (
                        (
                            "Broad Any removes the checks that would expose "
                            "inconsistent use."
                        ),
                        "Any is invalid Python syntax.",
                        "Any always raises at runtime.",
                        "Any can only describe integers.",
                    ),
                    0,
                    "Any opts out of much of the type checker's useful reasoning.",
                ),
            ),
        ),
        (
            "foundations-automation-and-ci-challenge",
            "Automated Quality Gate readiness check",
            (
                (
                    "same-checks",
                    "Why should local and CI commands agree?",
                    (
                        (
                            "A learner can reproduce failures before and after "
                            "sharing a change."
                        ),
                        "CI then guarantees no bugs exist.",
                        "Local tests become unnecessary.",
                        "Every workflow runs faster.",
                    ),
                    0,
                    (
                        "One quality agreement reduces surprises between local work "
                        "and remote automation."
                    ),
                ),
                (
                    "ci-trigger",
                    "What should a basic pull-request workflow do?",
                    (
                        (
                            "Check out the code, prepare Python, install declared "
                            "tools, and run the agreed checks."
                        ),
                        "Publish without running tests.",
                        "Modify source files and commit them.",
                        "Depend on packages installed on a learner's laptop.",
                    ),
                    0,
                    (
                        "A clean runner must reconstruct the project before it can "
                        "verify the agreed checks."
                    ),
                ),
            ),
        ),
        (
            "foundations-object-oriented-programming-challenge",
            "Equipment Rental readiness check",
            (
                (
                    "composition",
                    "What should the rental service own?",
                    (
                        "A collection of equipment objects it coordinates.",
                        "Copies of every method as strings.",
                        "Only one unrelated global number.",
                        "The Python interpreter.",
                    ),
                    0,
                    (
                        "Composition lets the service coordinate cohesive item "
                        "objects without pretending it is an item."
                    ),
                ),
                (
                    "class-invariant",
                    "Where should an item's unavailable-state rule be protected?",
                    (
                        "At the method boundary that changes checkout state.",
                        "Only in the README.",
                        "In a caller's comment.",
                        "By renaming the class.",
                    ),
                    0,
                    (
                        "The object that owns the state should keep invalid "
                        "transitions from being represented silently."
                    ),
                ),
            ),
        ),
        (
            "foundations-comprehensions-and-iteration-challenge",
            "Sensor Stream readiness check",
            (
                (
                    "generator-lazy",
                    "What makes a generator suitable for a long sensor stream?",
                    (
                        "It can produce matching readings on demand.",
                        "It sorts every reading automatically.",
                        "It can never be exhausted.",
                        "It converts every reading to text.",
                    ),
                    0,
                    (
                        "Lazy iteration avoids building every possible result before "
                        "the caller needs it."
                    ),
                ),
                (
                    "readable-comprehension",
                    "When should a comprehension be replaced by an ordinary loop?",
                    (
                        (
                            "When the expression becomes difficult to explain or "
                            "needs several stateful steps."
                        ),
                        "Whenever it creates a list.",
                        "Whenever it has one condition.",
                        "Only when the input is empty.",
                    ),
                    0,
                    "Conciseness helps only while the transformation remains readable.",
                ),
            ),
        ),
        (
            "foundations-decorators-and-context-managers-challenge",
            "Managed Operation readiness check",
            (
                (
                    "wraps-purpose",
                    "Why use functools.wraps in a function decorator?",
                    (
                        "It preserves useful metadata from the wrapped function.",
                        "It guarantees the function never raises.",
                        "It converts arguments to strings.",
                        "It opens a file automatically.",
                    ),
                    0,
                    (
                        "wraps keeps metadata such as the original name and docstring "
                        "visible."
                    ),
                ),
                (
                    "cleanup-path",
                    "Where should context-manager cleanup run?",
                    (
                        (
                            "After both successful work and exceptions inside the "
                            "managed block."
                        ),
                        "Only when the block prints output.",
                        "Before setup.",
                        "Only when no resource was acquired.",
                    ),
                    0,
                    (
                        "The context boundary exists to pair setup with reliable "
                        "cleanup on every exit path."
                    ),
                ),
            ),
        ),
        (
            "foundations-logging-and-configuration-challenge",
            "Configurable Batch Processor readiness check",
            (
                (
                    "log-vs-output",
                    "What should logging provide in the batch processor?",
                    (
                        (
                            "Operational evidence for diagnosis without replacing "
                            "user-facing results."
                        ),
                        "Every value the user requested as hidden debug output.",
                        "A substitute for validation.",
                        "A guarantee that file access succeeds.",
                    ),
                    0,
                    (
                        "Logs describe operation; user-facing output communicates the "
                        "requested result."
                    ),
                ),
                (
                    "config-boundary",
                    (
                        "What should happen when configuration contains an "
                        "unsupported log level?"
                    ),
                    (
                        (
                            "Validation should report a clear boundary error before "
                            "processing starts."
                        ),
                        "The value should silently become valid.",
                        "Every exception should be ignored.",
                        "The program should edit its own source code.",
                    ),
                    0,
                    (
                        "Explicit validation prevents invalid settings from spreading "
                        "into later behavior."
                    ),
                ),
            ),
        ),
    )
    return tuple(_quiz_from_spec(spec) for spec in specs)


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
