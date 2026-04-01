from openai import OpenAI
import os
from config import SUMMARY_MODEL_NAME

client = OpenAI(api_key=os.getenv("OpenAI_API_KEY"))

summary_prompt= """
You are a system that summarizes industrial conversations.
Summarize the conversation into a concise state summary.
Focus on:
- current issue
- responsible person
- current actions
- system status

Previous summary:
{old_summary}

New messages:
{new_messages}

Return ONLY the updated summary.
"""

def update_summary(chat_history, old_summary):
    recent = chat_history[-8:]
    messages_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent])

    prompt = summary_prompt.format(old_summary=old_summary, new_messages=messages_text)

    response = client.chat.completions.create(
        model=SUMMARY_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()