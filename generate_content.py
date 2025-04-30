from dotenv import load_dotenv
import openai
import os


# Make sure API key is set
load_dotenv()

# initialize client
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

class QuizRationaleGenerator:
    def __init__(self, model="gpt-4-turbo"):
        self.model = model

    def create_prompt(self, question_block, existing_rationales=None):
        """
        Build the full system/user prompt for a question block
        """
        user_content = f"""Given the following multiple-choice question and answer options, please generate a single, consolidated rationale that succinctly explains why the correct option is correct and the incorrect options are incorrect. The rationale should ideally have no more than one sentence per answer option, but it may have fewer. If you refer to answer options specifically in the rationale, you can do so by referring to the option letter in parentheses (e.g. "ETL (option B) is not...") after mentioning the concept it represents. Where letters are concerned, the first option is A, the second is B, etc. You do not necessarily need to specifically state which options are correct or incorrect, as the reader will see this information elsewhere. Do not use hyphens to precede or separate the rationale elements. The rationale should be a single paragraph.

Here is the question:

{question_block}
"""
        if existing_rationales:
            user_content += "\n Existing Rationales (each corresponds to a question option):\n"
            user_content += f"{existing_rationales}\n"
            user_content += "\nYou should adapt these in the consolidated rationale you provide."
        return [
            {"role": "system", "content": "You are an expert educational content writer. You write clear rationales for quiz questions."},
            {"role": "user", "content": user_content}
        ]

    def generate_rationale(self, question_block, existing_rationales=None, temperature=0.5):
        """
        Generates a consolidated rationale string for question.
        """
        messages = self.create_prompt(question_block, existing_rationales)

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    