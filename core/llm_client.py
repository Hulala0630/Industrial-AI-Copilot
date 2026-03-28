from openai import OpenAI
from dotenv import load_dotenv
import os
import json

from config import MODEL_NAME
from core.tools import get_system_state
from core.tools import get_active_alarms

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def ask_llm(user_input):

    system_state = get_system_state()
    active_alarms = get_active_alarms()

    response =client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"""
                You are an industrial diagnostic assistant.
                
                Current system state:
                {json.dumps(system_state, indent=2)}
                Active alarms:
                {json.dumps(active_alarms, indent=2)}
                
                Analyze the user's question based on the current system state and active alarms.
                Provide:
                1. possible cause
                2. alarm explanation
                3. suggested action
                """
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )
    
    return response.choices[0].message.content