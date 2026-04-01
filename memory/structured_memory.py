from openai import OpenAI
from config import MEMORY_MODEL_NAME
import os
import json

client =OpenAI(api_key=os.getenv("OpenAI_API_KEY"))

memory_prompt = """
Extract structured memory from the conversation.

Return JSON only.

Schema:
{{
  "current_line": "",
  "active_alarm": {{
    "id": "",
    "name": "",
    "severity": ""
  }},
  "responsible_person": "",
  "next_action": "",
  "user_goal": ""
}}

Conversation:
{conversation}
"""


def update_structured_memory(chat_history, old_memory):
   
    recent = chat_history[-8:]

    messages_text = "\n".join([
        f"{m['role']}: {m['content']}"
        for m in recent
    ])

    prompt = memory_prompt.format(conversation=messages_text)

    response = client.chat.completions.create(
        model=MEMORY_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        new_memory = json.loads(response.choices[0].message.content)

        merged = {**old_memory, **new_memory}
        return merged

    except:
        return old_memory