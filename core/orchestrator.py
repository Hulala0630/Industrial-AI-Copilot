from copy import deepcopy

from core.replanner import Replanner
from core.executor import Executor
from memory.summary_manager import update_summary
from memory.structured_memory import update_structured_memory
from memory.context_builder import build_messages
from core.planner import Planner



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


def _build_base_messages(user_input: str, session_state) -> list:
    system_prompt = load_system_prompt()

    return build_messages(
        system_prompt=system_prompt,
        summary=session_state["summary"],
        memory=session_state["memory"],
        chat_history=session_state["full_chat_history"][-8:],
        user_input=user_input
    )


def _apply_replan_to_plan(original_plan: dict, review_result: dict) -> dict:
    """
    Lightweight replan strategy:
    - keep original plan structure
    - replace goal/tools if reviewer provides revised values
    """
    new_plan = deepcopy(original_plan)

    revised_goal = review_result.get("revised_goal", "")
    revised_tools = review_result.get("revised_tools", [])

    if revised_goal:
        new_plan["goal"] = revised_goal

    if isinstance(revised_tools, list) and revised_tools:
        new_plan["tools"] = revised_tools
        new_plan["need_tools"] = True

    return new_plan


def run_agent_turn(user_input, session_state):
    initialize_session_state(session_state)

    planner = Planner()
    executor = Executor()
    replanner = Replanner()

    session_state["turn_count"] += 1
    turn_count = session_state["turn_count"]

    trace = {
        "turn_count": turn_count,
        "user_input": user_input,
        "pre_turn_state": {
            "summary": session_state["summary"],
            "memory": deepcopy(session_state["memory"])
        },
        "initial_plan": None,
        "execution_result": None,
        "review_result": None,
        "replan_used": False,
        "replanned_plan": None,
        "replanned_execution_result": None,
        "replanned_review_result": None,
        "steps": [],
        "post_turn_state": {},
        "final_answer": ""
    }

  
    base_messages = _build_base_messages(user_input, session_state)
    trace["steps"].append({
        "step": "build_context",
        "detail": {
            "recent_chat_count": len(session_state["full_chat_history"][-8:]),
            "summary_present": bool(session_state["summary"]),
            "memory_present": bool(session_state["memory"])
        }
    })

   
    plan = planner.plan(
        user_input=user_input,
        summary=session_state["summary"],
        memory=session_state["memory"]
    )
    trace["initial_plan"] = deepcopy(plan)
    trace["steps"].append({
        "step": "planner",
        "detail": deepcopy(plan)
    })

   
    execution_result = executor.execute(plan, base_messages)
    trace["execution_result"] = {
        "status": execution_result.get("status"),
        "tools_used": execution_result.get("tools_used", []),
        "observations": execution_result.get("observations", [])
    }
    trace["steps"].append({
        "step": "executor",
        "detail": {
            "status": execution_result.get("status"),
            "tools_used": execution_result.get("tools_used", []),
            "tool_count": len(execution_result.get("tools_used", [])),
            "observations": execution_result.get("observations", [])
        }
    })

    review_result = replanner.review(
        user_input=user_input,
        plan=plan,
        execution_result=execution_result
    )
    trace["review_result"] = deepcopy(review_result)
    trace["steps"].append({
        "step": "reviewer",
        "detail": deepcopy(review_result)
    })

    final_execution_result = execution_result

    if review_result.get("action") == "replan":
        trace["replan_used"] = True

        replanned_plan = _apply_replan_to_plan(plan, review_result)
        trace["replanned_plan"] = deepcopy(replanned_plan)
        trace["steps"].append({
            "step": "replan",
            "detail": deepcopy(replanned_plan)
        })

        replanned_execution_result = executor.execute(replanned_plan, base_messages)
        trace["replanned_execution_result"] = {
            "status": replanned_execution_result.get("status"),
            "tools_used": replanned_execution_result.get("tools_used", []),
            "observations": replanned_execution_result.get("observations", [])
        }
        trace["steps"].append({
            "step": "executor_replanned",
            "detail": {
                "status": replanned_execution_result.get("status"),
                "tools_used": replanned_execution_result.get("tools_used", []),
                "tool_count": len(replanned_execution_result.get("tools_used", [])),
                "observations": replanned_execution_result.get("observations", [])
            }
        })

        replanned_review_result = replanner.review(
            user_input=user_input,
            plan=replanned_plan,
            execution_result=replanned_execution_result
        )
        trace["replanned_review_result"] = deepcopy(replanned_review_result)
        trace["steps"].append({
            "step": "reviewer_replanned",
            "detail": deepcopy(replanned_review_result)
        })

        final_execution_result = replanned_execution_result

 
    final_answer = final_execution_result.get("final_answer_candidate", "")
    trace["final_answer"] = final_answer


    session_state["full_chat_history"].append({
        "role": "user",
        "content": user_input
    })
    session_state["full_chat_history"].append({
        "role": "assistant",
        "content": final_answer,
        "tools_used": final_execution_result.get("tools_used", []),
        "tool_results": final_execution_result.get("tool_results", {}),
        "observations": final_execution_result.get("observations", [])
    })

 
    summary_updated = False
    memory_updated = False
    if turn_count % 3 == 0:  # Update memory every 2 turns to reduce cost
        session_state["summary"] = update_summary(
            chat_history=session_state["full_chat_history"],
            old_summary=session_state["summary"]
        )
        summary_updated = True

        session_state["memory"] = update_structured_memory(
            chat_history=session_state["full_chat_history"],
            old_memory=session_state["memory"]
        )
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
        "memory": deepcopy(session_state["memory"])
    }


    session_state["last_trace"] = trace
    session_state["trace_history"].append(trace)

    return {
        "answer": final_answer,
        "tools_used": final_execution_result.get("tools_used", []),
        "tool_results": final_execution_result.get("tool_results", {}),
        "observations": final_execution_result.get("observations", []),
        "trace": trace
    }