import json
import re
from openai import OpenAI
from dotenv import load_dotenv
import os
from config import REPLANNER_MODEL_NAME

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_replanner_prompt():
    with open("prompts/replanner_prompt.md", "r", encoding="utf-8") as f:
        return f.read()


def extract_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return text


class Replanner:
    def __init__(self, model_name=REPLANNER_MODEL_NAME):
        self.model_name = model_name

    def review(self, user_input: str, plan: dict, execution_result: dict) -> dict:
        system_prompt = load_replanner_prompt()

        response = client.chat.completions.create(
            model=self.model_name,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "user_input": user_input,
                            "plan": plan,
                            "execution_result": execution_result
                        },
                        ensure_ascii=False,
                        indent=2
                    )
                }
            ]
        )

        raw = response.choices[0].message.content or ""
        cleaned = extract_json(raw)

        try:
            decision = json.loads(cleaned)
        except Exception:
            decision = {
                "action": "final_answer",
                "reason": "Fallback to final answer due to reviewer parse failure.",
                "revised_goal": "",
                "revised_tools": []
            }

        decision.setdefault("action", "final_answer")
        decision.setdefault("reason", "")
        decision.setdefault("revised_goal", "")
        decision.setdefault("revised_tools", [])

        return decision