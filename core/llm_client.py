from openai import OpenAI
from dotenv import load_dotenv
import os
import json

from config import MODEL_NAME
from core.tools_definitions import tools
from core.tools import get_system_state
from core.tools import get_active_alarms

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def execute_tool(tool_name):
    if tool_name == "get_system_state":
        return get_system_state()
    elif tool_name == "get_active_alarms":
        return get_active_alarms()
    else:
        return {"error": f"Unknown tool: {tool_name}"}
    

def ask_llm(user_input):

    messages=[
            {
                "role": "system", 
                "content": "You are an industrial assistant."},
            {
                "role": "user",
                "content": user_input
            }
        ]
    # Step 1: initial response from the assistant, which may include tool calls
    response =client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
    )
    message = response.choices[0].message
    
    # If there are no tool calls, return the assistant's response directly
    if not message.tool_calls:
        return message.content
    
    # If there are tool calls, we need to execute them and then send the results back to the assistant for a second response
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

    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        tool_result = execute_tool(tool_name)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result, ensure_ascii=False)
            }
        )

    second_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages
    )

    return second_response.choices[0].message.content