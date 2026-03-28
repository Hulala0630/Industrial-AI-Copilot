from openai import OpenAI
from dotenv import load_dotenv
import os

from config import MODEL_NAME
from core.tools import get_system_state

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def ask_llm(user_input):

    system_state = get_system_state()

    response =client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": f"""
             You are an industrial assistant. 
             The current system state is: {system_state}
             analyze the system state and answer the user's question based on the system state.
             """},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content