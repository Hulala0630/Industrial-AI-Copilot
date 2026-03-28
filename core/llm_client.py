from openai import OpenAI
from config import MODEL_NAME
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def ask_llm(user_input):
    response =client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are an industrial assistant."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content