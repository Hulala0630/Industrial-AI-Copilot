import json


def build_messages(
    system_prompt: str,
    summary: str,
    memory: dict,
    chat_history: list,
    user_input: str
):
    messages = []

    messages.append({
        "role": "system",
        "content": system_prompt
    })

    memory_block = f"""
Conversation Summary:
{summary}

Structured Memory:
{json.dumps(memory, ensure_ascii=False, indent=2)}
"""

    messages.append({
        "role": "system",
        "content": memory_block
    })

    for msg in chat_history[-8:]:
        messages.append(msg)

    messages.append({
        "role": "user",
        "content": user_input
    })

    return messages