
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re
from config import PLAN_MODEL_NAME

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_planner_prompt():
    with open("prompts/planner_prompt.md", "r", encoding="utf-8") as f:
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

class Planner:
    
    def __init__(self, model_name=PLAN_MODEL_NAME):
        self.model_name = model_name

    def plan(self, user_input: str, summary: str = "", memory: dict | None = None) -> dict:
        memory = memory or {}

        system_prompt = load_planner_prompt()

        response = client.chat.completions.create(
            model=self.model_name,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps({
                        "user_input": user_input,
                        "summary": summary,
                        "memory": memory
                    }, ensure_ascii=False, indent=2)
                }
            ]
        )

        raw = response.choices[0].message.content or ""
        cleaned = extract_json(raw)

        try:
            plan = json.loads(cleaned)
        except Exception:
            plan = {
                "intent": "general_response",
                "skill": "general_response",
                "target_entity": "",
                "need_tools": False,
                "tools": [],
                "success_criteria": "Provide a direct answer if possible.",
                "reason": "Fallback plan due to JSON parse failure."
            }

        plan.setdefault("intent", "general_response")
        plan.setdefault("skill", "general_response")
        plan.setdefault("target_entity", "")
        plan.setdefault("need_tools", False)
        plan.setdefault("tools", [])
        plan.setdefault("success_criteria", "")
        plan.setdefault("reason", "")

        if not isinstance(plan["tools"], list):
            plan["tools"] = []

        return plan