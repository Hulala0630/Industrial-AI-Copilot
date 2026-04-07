from openai import OpenAI
from dotenv import load_dotenv
import os
import json

from config import MAIN_MODEL_NAME
from core.tools_definitions import tools
from core.tools import get_system_state
from core.tools import get_active_alarms
from core.tools import get_production_context

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def execute_tool(tool_name):
    if tool_name == "get_system_state":
        return get_system_state()
    elif tool_name == "get_active_alarms":
        return get_active_alarms()
    elif tool_name == "get_production_context":
        return get_production_context()
    else:
        return {"error": f"Unknown tool: {tool_name}"}
    
def load_system_prompt():
    with open("prompts/system_prompt.md", "r", encoding="utf-8") as f:
        return f.read()
    
def ask_llm(messages, available_tools=None):

    response =client.chat.completions.create(
        model=MAIN_MODEL_NAME,
        messages=messages,
        tools=available_tools if available_tools is not None else tools,
    )
    message = response.choices[0].message

    if not message.tool_calls:
        return {
        "answer": message.content,
        "tools_used": [],
        "tool_results": {}
    }
    
    assistant_message = {
        "role": "assistant",
        "content": message.content or "",
        "tool_calls": []
    }

    for tool_call in message.tool_calls:
        assistant_message["tool_calls"].append(
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            }
        )

    messages.append(assistant_message)
    
    tools_used = []
    tool_results = {}
    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        tool_result = execute_tool(tool_name)

        tools_used.append(tool_name)
        tool_results[tool_name] = tool_result

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result, ensure_ascii=False)
            }
        )

    second_response = client.chat.completions.create(
        model=MAIN_MODEL_NAME,
        messages=messages
    )
    
    final_answer = second_response.choices[0].message.content
    return {
        "answer": final_answer,
        "tools_used": tools_used,
        "tool_results": tool_results
    }