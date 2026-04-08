from config import MAIN_MODEL_NAME
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def complete(messages, tools=None, temperature=0):
    response = client.chat.completions.create(
        model=MAIN_MODEL_NAME,
        messages=messages,
        tools=tools,
        temperature=temperature
    )
    return response.choices[0].message