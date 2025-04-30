# Answer-Key Appendix from Quiz Markdown

Script for generating an answer-key appendix Markdown file of quiz question answers from a Markdown file containing quizzes. It leverages an AI service to consolidate any existing question rationales into a single string (or to create a new rationale), prepended by the correct answer(s) in letter format. For use when incorporating interactive quiz content into hardcopy book content.

For converting a quiz DOCX to quiz Markdown, see the [quiz-docx-to-markdown](https://github.com/ghyman-oreilly/quiz-docx-to-markdown) script. If you need access to that private repo, contact Greg Hyman.

### Requirements

- Python 3.7+
- OpenAI API key (contact Greg Hyman for key)

## Installation and setup

1. Clone down the repo and cd into the project root.

2. Install dependencies: `pip install -r requirements.txt`

3. Create a `.env` file in the root directory to store the credentials for the OpenAI service:

```bash
echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env
```

## Usage

1. Run the `main.py` script:
   
   ```python main.py <path_to_markdown_file> [--output-dir]```
    
2. Running the script will produce an appendix Markdown file from your quiz Markdown file. 

3. Use a CLI tool such as [pandoc](https://pandoc.org) to convert the Markdown to HTML, if/as needed.

## Script options

* `--output-dir`: Set a custom output directory. Defaults to `./data`.

## Resources

* See `media/md_quiz_structure.md` for expected quiz Markdown structure.
* [quiz-docx-to-markdown script](https://github.com/ghyman-oreilly/quiz-docx-to-markdown)
