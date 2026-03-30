from core.tools import get_system_state, get_active_alarms


def decide_and_execute(user_input):
    
    user_input_lower = user_input.lower()

    if "alarm" in user_input_lower:
        tool_result = get_active_alarms()
        tool_name = "get_active_alarms"

    elif "state" in user_input_lower or "status" in user_input_lower:
        tool_result = get_system_state()
        tool_name = "get_system_state"

    else:
        tool_result = None
        tool_name = None

    return tool_name, tool_result