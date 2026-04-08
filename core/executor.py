from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re

from core.llm_client import complete
from core.tools_definitions import get_tools_by_names
from core.tool_executor import execute_tool
from config import EXECUTE_MODEL_NAME

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_executor_prompt():
    with open("prompts/executor_prompt.md", "r", encoding="utf-8") as f:
        return f.read()
def load_observation_prompt():
    with open("prompts/observation_prompt.md","r", encoding="utf-8") as f:
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
class Executor:
    def execute(self, plan: dict, base_messages: list) -> dict:
        allowed_tools = get_tools_by_names(plan["tools"]) if plan.get("need_tools") else []

        messages = list(base_messages)
        messages.insert(1, {
            "role": "system",
            "content": load_executor_prompt()
        })
        messages.insert(2, {
            "role": "system",
            "content": f"Execution Plan:\n{json.dumps(plan, ensure_ascii=False, indent=2)}"
        })

        first_message = complete(messages=messages, tools=allowed_tools, temperature=0)

        tools_used = []
        tool_results = {}

        if first_message.tool_calls:
            assistant_message = {
                "role": "assistant",
                "content": first_message.content or "",
                "tool_calls": []
            }

            for tool_call in first_message.tool_calls:
                assistant_message["tool_calls"].append({
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                })

            messages.append(assistant_message)

            for tool_call in first_message.tool_calls:
                tool_name = tool_call.function.name
                tool_result = execute_tool(tool_name)

                tools_used.append(tool_name)
                tool_results[tool_name] = tool_result

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })

            # 2nd model call
            second_message = complete(messages=messages, temperature=0)
            
            final_answer_candidate = second_message.content or ""
        else:
            final_answer_candidate = first_message.content or ""

        observations = self._build_observations(tool_results)

        return {
            "status": "success",
            "tools_used": tools_used,
            "tool_results": tool_results,
            "observations": observations,
            "final_answer_candidate": final_answer_candidate
        }

    def _build_observations(self, tool_results: dict) -> list[str]:
        observations = []

        if "get_system_state" in tool_results:
            observations.append("System state data was retrieved.")

        if "get_active_alarms" in tool_results:
            observations.append("Active alarm data was retrieved.")

        if "get_production_context" in tool_results:
            observations.append("Production context data was retrieved.")

        return observations