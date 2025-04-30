from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class QuizType(Enum):
    FORMATIVE = "Formative"
    SUMMATIVE = "Summative"


@dataclass
class Quiz:
    title: str
    quiz_type: Optional['QuizType'] = None
    questions: List['Question'] = field(default_factory=list)

    def set_quiz_type(self, quiz_type):
        self.quiz_type = quiz_type

    def add_question(self, question: 'Question'):
        self.questions.append(question)
        

@dataclass
class Question:
    question_stem_str: str = ''
    question_options: list['QuestionOption'] = field(default_factory=list)
    question_rationales: list['QuestionRationale'] = field(default_factory=list)
    question_markdown_str: str = ''
    answer_key_options_str: str = ''
    generated_consolidated_rationale_str: str = ''

    def set_question_stem_str(self, question_stem_str):
        self.question_stem_str = question_stem_str

    def add_question_option(self, question_option: 'QuestionOption'):
        self.question_options.append(question_option)

    def add_question_rationale(self, question_rationale: 'QuestionRationale'):
        self.question_rationales.append(question_rationale)
    
    def generate_options_str(self) -> str:
        """
        Returns a Markdown string for the list of options,
        marking correct ones with [x] and incorrect ones with [ ].
        """
        lines = []
        for option in self.question_options:
            check_mark = "[x]" if option.is_correct else "[ ]"
            # Handle multiline option strings by indenting wrapped lines
            option_lines = option.question_option_str.strip().splitlines()
            if option_lines:
                first_line = f"- {check_mark} {option_lines[0]}"
                following_lines = [f"  {line}" for line in option_lines[1:]]
                lines.append(first_line)
                lines.extend(following_lines)
            else:
                # Just in case there's a blank string
                lines.append(f"- {check_mark}")
        return "\n".join(lines)

    def generate_rationales_str(self) -> str:
        """
        Returns a Markdown-formatted string for the list of rationales.
        Multi-line rationales are preserved as-is, separated by line breaks.
        """
        lines = []
        for rationale in self.question_rationales:
            rationale_text = rationale.question_rationale_str.strip()
            if rationale_text:
                lines.append(rationale_text)
        return "\n\n".join(lines)


@dataclass
class QuestionOption:
    question_option_str: str = ''
    is_correct: bool = False


@dataclass
class QuestionRationale:
    question_rationale_str: str = ''


Quizzes = list[Quiz]

def generate_and_set_answer_key_options_str(question: Question):
    def index_to_letter(index: int) -> str:
        return chr(ord('A') + index)

    answer_key_entries = []

    correct_letters = [
        index_to_letter(i)
        for i, option in enumerate(question.question_options)
        if option.is_correct
    ]
    entry = ", ".join(correct_letters)
    answer_key_entries.append(entry)

    question.answer_key_options_str = "\n".join(answer_key_entries)