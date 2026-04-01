from core.llm_client import ask_llm
from memory.summary_manager import update_summary
from memory.structured_memory import update_structured_memory
from memory.context_builder import build_messages

def load_system_prompt():
    with open("prompts/system_prompt.md", "r", encoding="utf-8") as f:
        return f.read()
    
def initialize_session_state(session_state):
    if "chat_history" not in session_state:
        session_state["chat_history"] = []

    if "summary" not in session_state:
        session_state["summary"] = ""

    if "memory" not in session_state:
        session_state["memory"] = {}
    
    if "turn_count" not in session_state:
        session_state["turn_count"] = 0
    
    if "last_trace" not in session_state:
        session_state["last_trace"] = None

def run_agent_turn(user_input, session_state):
    
    
    initialize_session_state(session_state)

    session_state["turn_count"] += 1
    turn_count = session_state["turn_count"]
    
    trace = {
    "user_input": user_input,
    "turn_count": session_state["turn_count"],
    "used_summary": session_state.get("summary", ""),
    "used_memory": session_state.get("memory", {}),
    "steps": [],
    "final_answer": ""
    }
    

    system_prompt = load_system_prompt()
    trace["steps"].append({
        "step": "load_system_prompt",
        "detail": "Loaded system prompt from prompts/system_prompt.md"
    })

    messages = build_messages(
        system_prompt=system_prompt,
        summary=session_state["summary"],
        memory=session_state["memory"],
        chat_history=session_state["chat_history"],
        user_input=user_input
    )

    result = ask_llm(messages)

    trace["steps"].append({
        "step": "llm_and_tools",
        "detail": {
            "tools_used": result["tools_used"],
            "tool_count": len(result["tools_used"])
        }
    })

    session_state["chat_history"].append({
        "role": "user",
        "content": user_input
    })
    session_state["chat_history"].append({
        "role": "assistant",
        "content": result["answer"],
        "tools_used": result["tools_used"],
        "tool_results": result["tool_results"],
        "trace": trace
    })

    session_state["chat_history"] = session_state["chat_history"][-8:]
    
    if turn_count % 3 == 0:
        session_state["summary"] = update_summary(chat_history=session_state["chat_history"],
                                              old_summary=session_state["summary"])
      
    
        session_state["memory"] = update_structured_memory(chat_history=session_state["chat_history"],
                                                        old_memory=session_state["memory"])
 
    
    
    
    return result
    

