from core.executor import Executor
from core.llm_client import ask_llm
from memory.summary_manager import update_summary
from memory.structured_memory import update_structured_memory
from memory.context_builder import build_messages
from core.planner import Planner
from core.tools_definitions import get_tools_by_names 



def load_system_prompt():
    with open("prompts/system_prompt.md", "r", encoding="utf-8") as f:
        return f.read()
    
def initialize_session_state(session_state):
    if "full_chat_history" not in session_state:
        session_state["full_chat_history"] = []

    if "summary" not in session_state:
        session_state["summary"] = ""

    if "memory" not in session_state:
        session_state["memory"] = {}
    
    if "turn_count" not in session_state:
        session_state["turn_count"] = 0
    
    if "last_trace" not in session_state:
        session_state["last_trace"] = None

    if "trace_history" not in session_state:
        session_state["trace_history"] = []

def run_agent_turn(user_input, session_state):
    
    planner = Planner()
    executor = Executor()
    
    initialize_session_state(session_state)

    session_state["turn_count"] += 1
    turn_count = session_state["turn_count"]
    
    trace = {
    "turn_count": turn_count,
    "user_input": user_input,
    "pre_turn_state": {
        "summary": session_state["summary"],
        "memory": session_state["memory"]
    },
    "plan": None,
    "steps": [],
    "post_turn_state": {},
    "final_answer": ""
    }

    system_prompt = load_system_prompt()

    trace["steps"].append({
        "step": "load_system_prompt",
        "detail": "Loaded system prompt from prompts/system_prompt.md"
    })

    plan = planner.plan(
    user_input=user_input,
    summary=session_state["summary"],
    memory=session_state["memory"]
    )

    trace["plan"] = plan
    trace["steps"].append({
        "step": "planner",
        "detail": plan
    })

    messages = build_messages(
        system_prompt=system_prompt,
        summary=session_state["summary"],
        memory=session_state["memory"],
        chat_history=session_state["full_chat_history"][-8:],
        user_input=user_input
    )
    
    trace["steps"].append({
        "step": "build_context",
        "detail": {
            "recent_chat_count": len(session_state["full_chat_history"][-8:]),
            "summary_present": bool(session_state["summary"]),
            "memory_present": bool(session_state["memory"])
        }
    })

    execution_result = executor.execute(plan, messages)
    trace["execution_result"] = {
        "status": execution_result["status"],
        "tools_used": execution_result["tools_used"]
    }
    trace["steps"].append({
        "step": "executor",
        "detail": {
            "tools_used": execution_result["tools_used"],
            "tool_count": len(execution_result["tools_used"])
        }
    })

    final_answer = execution_result["final_answer"]

    
    session_state["full_chat_history"].append({
        "role": "user",
        "content": user_input
    })
   
    session_state["full_chat_history"].append({
        "role": "assistant",
        "content": final_answer,
        "tools_used": execution_result["tools_used"],
        "tool_results": execution_result["tool_results"]
    })
    
    summary_updated = False
    memory_updated = False
    if turn_count % 3 == 0:
        session_state["summary"] = update_summary(chat_history=session_state["full_chat_history"],
                                              old_summary=session_state["summary"])
        summary_updated = True
      
    
        session_state["memory"] = update_structured_memory(chat_history=session_state["full_chat_history"],
                                                        old_memory=session_state["memory"])
        memory_updated = True

        trace["steps"].append({
        "step": "memory_update",
        "detail": {
            "summary_updated": summary_updated,
            "structured_memory_updated": memory_updated
        }
        })
 
    trace["post_turn_state"] = {
        "summary": session_state["summary"],
        "memory": session_state["memory"]
    }

    trace["final_answer"] = final_answer

    session_state["last_trace"] = trace
    session_state["trace_history"].append(trace)
    
    
    return {
        "answer": final_answer,
        "tools_used": execution_result["tools_used"],
        "tool_results": execution_result["tool_results"],
        "trace": trace
    }
    

