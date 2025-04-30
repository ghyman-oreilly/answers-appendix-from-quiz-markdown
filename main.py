import argparse
import os
from pathlib import Path
import time

from generate_content import QuizRationaleGenerator
from parse_markdown import parse_markdown_to_quizzes, write_answer_key_markdown_from_quizzes
from quizzes import Question


def generate_and_set_consolidated_rationales(question: Question):
	"""
	Update Question instance with consolidate rationale generated
	by generative AI service.
	"""
	rationale_generator = QuizRationaleGenerator()

	question_content = f"{question.question_stem_str}\n{question.generate_options_str()}"
	old_rationale_str = question.generate_rationales_str()
	new_rationale_str = rationale_generator.generate_rationale(question_content, existing_rationales=(old_rationale_str if old_rationale_str != '' else None))
	new_rationale_str = new_rationale_str.replace('\n\n','\n')
	question.generated_consolidated_rationale_str = new_rationale_str
	time.sleep(1) # Pause 1 second between API calls


def main():
	"""
	Script for generating an appendix file of quiz answers from a quiz markdown file. 
	"""
	parser = argparse.ArgumentParser(description="Script for generating an appendix file of quiz answers from a quiz markdown file.")
	parser.add_argument('markdown_file', help='Path to your Markdown file.')
	parser.add_argument('--output-dir', '-o', default='./data', help='Optional: Path to output directory. Default: ./data')

	args = parser.parse_args()

	if not args.markdown_file:
		raise ValueError("Path to Markdown file is required.")
	
	markdown_filepath = Path(args.markdown_file)
	output_dir = Path(args.output_dir)

	if (
		not markdown_filepath.exists() or
		not markdown_filepath.is_file() or
		not markdown_filepath.suffix[1:].lower() == 'md'
		):
		raise ValueError("Input must be path to a valid Markdown (.md) file.")

	if markdown_filepath.exists() and not output_dir.is_dir():
		raise ValueError("Output directory must be a directory.")
	
	if not output_dir.exists():
		os.makedirs(output_dir)

	with open(markdown_filepath, 'r') as f:
		input_markdown_str = f.read()

	print("Parsing quiz data from markdown...")

	quizzes = parse_markdown_to_quizzes(input_markdown_str)

	for i, quiz in enumerate(quizzes):
		for j, question in enumerate(quiz.questions):
			print(f"Generating consolidated rationale for question {j+1} of {len(quiz.questions)} in quiz {i+1} of {len(quizzes)}...")
			generate_and_set_consolidated_rationales(question)

	output_markdown_str = write_answer_key_markdown_from_quizzes(quizzes)

	output_filepath = Path(output_dir, f"{markdown_filepath.stem}_{int(time.time())}.md") 

	with open(output_filepath, 'w') as f:
		f.write(output_markdown_str)

	print("Script completed.")
	print(f"Markdown saved to {output_filepath}")


if __name__ == '__main__':
	main()
