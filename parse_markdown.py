import re

from quizzes import (
    Quiz, 
    QuizType, 
    Quizzes, 
    Question, 
    QuestionOption, 
    QuestionRationale, 
    generate_and_set_answer_key_options_str
    )


def parse_markdown_to_quizzes(markdown_str: str) -> Quizzes:
    """
    Generate a Quizzes list from a Markdown string,
    parsing quizzes with titles, types, questions,
    stems, options, and rationales.
    """
    quizzes: Quizzes = []
    quiz = None
    question = None
    current_question_lines = []
    current_stem_lines = []
    current_option_lines = []
    current_options = []
    current_rationale_lines = []
    current_rationales = []
    current_mode = None  # None, 'stem', 'options', or 'rationales'

    markdown_lines = markdown_str.split('\n')

    def flush_current_option():
        nonlocal current_option_lines, current_option_is_correct, current_options
        if current_option_lines:
            option_text = "\n".join(current_option_lines).strip()
            current_options.append(QuestionOption(question_option_str=option_text, is_correct=current_option_is_correct))
            current_option_lines = []
            current_option_is_correct = False  # reset after use

    def flush_current_rationale():
        nonlocal current_rationale_lines, current_rationales
        if current_rationale_lines:
            rationale_text = "\n".join(current_rationale_lines).strip()
            current_rationales.append(rationale_text)
            current_rationale_lines = []

    def flush_current_question():
        nonlocal question, quiz
        if quiz and question:
            stem = "\n".join(current_stem_lines).strip()
            if stem:
                question.set_question_stem_str(stem)

            flush_current_option()
            for option in current_options:
                question.add_question_option(option)

            flush_current_rationale()
            for rationale_text in current_rationales:
                question.add_question_rationale(QuestionRationale(question_rationale_str=rationale_text))

            # Store full question markdown
            full_question_markdown = "\n".join(current_question_lines).strip()
            question.question_markdown_str = full_question_markdown

            quiz.add_question(question)

        reset_current_question_buffers()

    def reset_current_question_buffers():
        nonlocal question, current_stem_lines, current_options
        nonlocal current_rationales, current_option_lines, current_rationale_lines
        nonlocal current_mode, current_question_lines
        question = None
        current_stem_lines = []
        current_options = []
        current_rationales = []
        current_option_lines = []
        current_rationale_lines = []
        current_mode = None
        current_question_lines = []

    def start_new_question():
        nonlocal question, current_mode
        flush_current_question()
        question = Question()
        current_mode = 'stem'

    def flush_current_quiz():
        nonlocal quiz, quizzes
        if quiz:
            flush_current_question()
            quizzes.append(quiz)

    for i, line in enumerate(markdown_lines):
        line = line.rstrip()

        if re.match(r'^# Title', line, flags=re.IGNORECASE):
            flush_current_quiz()
            quiz = Quiz(title=markdown_lines[i + 1].strip())
            current_mode = None

        elif re.match(r'^## Quiz Type', line, flags=re.IGNORECASE):
            if quiz:
                quiz_type_raw = markdown_lines[i + 1].strip()
                try:
                    quiz.set_quiz_type(QuizType(quiz_type_raw))
                except ValueError:
                    raise ValueError(f"Invalid quiz type '{quiz_type_raw}' at line {i}")
                current_mode = None

        elif re.match(r'^### Question', line, flags=re.IGNORECASE):
            start_new_question()
            current_question_lines.append(line)

        elif re.match(r'^### Rationale', line, flags=re.IGNORECASE):
            flush_current_option()  # in case rationale follows options
            current_mode = 'rationales'

        elif re.match(r'^-\s*\[(?:\s*|x)\]', line, re.IGNORECASE):
            if question:
                if current_mode != 'options':
                    flush_current_option()
                    current_mode = 'options'
                else:
                    flush_current_option()
                # Start a new option
                match = re.match(r'^-\s*\[(\s*|x)\](.*)$', line, re.IGNORECASE)
                if match:
                    marker = match.group(1).strip().lower()
                    option_text = match.group(2).strip()
                    is_correct = marker == 'x'
                    flush_current_option()
                    current_option_lines = [option_text]
                    current_option_is_correct = is_correct

        else:
            if question:
                current_question_lines.append(line)
                if current_mode == 'stem':
                    current_stem_lines.append(line)
                elif current_mode == 'options':
                    current_option_lines.append(line)
                elif current_mode == 'rationales':
                    # Treat blank lines as paragraph markers
                    if line.strip() == '':
                        flush_current_rationale()
                    else:
                        current_rationale_lines.append(line)

    flush_current_quiz()

    for quiz in quizzes:
        for question in quiz.questions:
            generate_and_set_answer_key_options_str(question)

    return quizzes


def write_quiz_markdown_from_quizzes(quizzes: Quizzes, use_consolidated_rationale_str=False) -> str:
    """
    Generate a Markdown quizzes string from Quizzes list.
    Option to use consolidated rationale string generated by AI service.
    """

    markdown_lines = []

    for quiz in quizzes:
        # Write Quiz Title
        markdown_lines.append("# Title")
        markdown_lines.append(quiz.title)
        markdown_lines.append("")  # Blank line for spacing

        # Write Quiz Type
        if quiz.quiz_type:
            markdown_lines.append("## Quiz Type")
            markdown_lines.append(quiz.quiz_type.value if quiz.quiz_type else '')
            markdown_lines.append("")

        for question in quiz.questions:
            # Write Question
            markdown_lines.append("### Question")
            markdown_lines.append(question.question_stem_str.strip())

            # Write Options
            if question.question_options:
                options_lines = question.generate_options_str().strip().split("\n")
                for option in options_lines:
                    markdown_lines.append(option.strip())
                markdown_lines.append("")  # Blank line after options

            # Write Rationales (if any)
            if question.question_rationales:
                markdown_lines.append("### Rationale")
                if use_consolidated_rationale_str:
                    rationales_lines = question.generated_consolidated_rationale_str().strip().split("\n")
                else:
                    rationales_lines = question.generate_rationales_str().strip().split("\n")
                for rationale in rationales_lines:
                    markdown_lines.append(rationale.strip())
                markdown_lines.append("")  # Blank line after rationale

        # Extra spacing between quizzes
        markdown_lines.append("")

    # Join all lines into final markdown text
    markdown_str = "\n".join(markdown_lines).strip()

    return markdown_str

def write_answer_key_markdown_from_quizzes(quizzes: Quizzes) -> str:
    """
    Generate a Markdown answer-key string from Quizzes list.
    """
    markdown_lines = []

    markdown_lines.append(f"# Answer Key")
    markdown_lines.append("")  # Blank line for spacing

    for quiz in quizzes:
        # Write Quiz Title
        markdown_lines.append(f"## {quiz.title}")
        markdown_lines.append("")  # Blank line for spacing

        for i, question in enumerate(quiz.questions):
            line = f"{i+1}. {question.answer_key_options_str}. {question.generated_consolidated_rationale_str}"
            markdown_lines.append(line.strip())

        # Extra spacing between quizzes
        markdown_lines.append("")

    # Join all lines into final markdown text
    markdown_str = "\n".join(markdown_lines).strip()

    return markdown_str
