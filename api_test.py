from openai import OpenAI
from dotenv import load_dotenv
import os

#Cle API
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#API
def chat_with_gpt(theme, nb_words):
    try:
        response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": f"Generate a Python list of dictionaries for vocabulary learning. Requirements: Each dictionary must have exactly two keys: 'lang1' and 'lang2', 'lang1' = english, 'lang2' = french, Theme: {theme}, Number of word pairs: {nb_words}, Words must be simple, common, and relevant to the theme, No duplicates Output format example: [dict('lang1': 'apple', 'lang2': 'pomme'),dict('lang1': 'banana', 'lang2': 'banane')] Return ONLY valid Python code (no explanations, no comments)"}]
            )
        chat_response = response['choices'][0]['message']['content']
        return chat_response
    except Exception as e:
        return f"An error occurred: {e}"

print(chat_with_gpt('birds', 3))