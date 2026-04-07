from core.llm_client import ask_llm
from core.tools_definitions import get_tools_by_names
from config import EXECUTE_MODEL_NAME

def load_executor_prompt():
    with open("prompts/executor_prompt.md", "r", encoding="utf-8") as f:
        return f.read()

class Executor:
    
    def execute(self, plan: dict, base_messages: list):
        allowed_tools = get_tools_by_names(plan["tools"]) if plan.get("need_tools") else []


        executor_messages = list(base_messages)
        executor_messages.insert(1, {
            "role": "system",
            "content": load_executor_prompt()
        })
        executor_messages.insert(2, {
            "role": "system",
            "content": f"Execution Plan:\n{plan}"
        })

        result = ask_llm(executor_messages, available_tools=allowed_tools)

        execution_result = {
            "status": "success",
            "tools_used": result["tools_used"],
            "tool_results": result["tool_results"],
            "observations": [],
            "final_answer": result["answer"]
        }

        return execution_result