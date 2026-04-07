from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re
from config import MEMORY_MODEL_NAME

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_PROMPT = """
You extract structured working memory for an industrial AI agent.

Return JSON only. Do not add markdown. Do not add explanation.

Schema:
{{
  "conversation_focus": "",
  "user_goal": "",
  "current_line": "",
  "active_alarm": {{
    "id": "",
    "name": "",
    "severity": ""
  }},
  "responsible_person": "",
  "next_action": "",
  "important_entities": []
}}

Conversation:
{conversation}
"""


def _extract_json_block(text: str) -> str:
    """
    Try to extract the first JSON object from model output.
    Handles cases like ```json ... ```
    """
    text = text.strip()

    # Remove markdown code fences if present
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # Try direct parse first
    try:
        json.loads(text)
        return text
    except Exception:
        pass

    # Fallback: grab first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    return text


def _deep_merge(old: dict, new: dict) -> dict:
    """
    Merge nested dicts while preserving old values when new values are empty.
    """
    result = dict(old)

    for key, value in new.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        elif value not in ("", None, [], {}):
            result[key] = value
        elif key not in result:
            result[key] = value

    return result


def update_structured_memory(chat_history, old_memory):
    recent = chat_history[-8:]

    messages_text = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in recent
    )

    prompt = MEMORY_PROMPT.format(conversation=messages_text)

    response = client.chat.completions.create(
        model=MEMORY_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw_text = response.choices[0].message.content or ""
    cleaned = _extract_json_block(raw_text)

    try:
        new_memory = json.loads(cleaned)
        if not isinstance(new_memory, dict):
            return old_memory
        merged = _deep_merge(old_memory or {}, new_memory)
        return merged
    except Exception as e:
        print("DEBUG structured_memory parse failed:", e)
        print("DEBUG raw structured_memory output:", raw_text)
        return old_memory