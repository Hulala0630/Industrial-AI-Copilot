from core.tools import get_system_state, get_active_alarms, get_production_context


def execute_tool(tool_name: str):
    if tool_name == "get_system_state":
        return get_system_state()
    elif tool_name == "get_active_alarms":
        return get_active_alarms()
    elif tool_name == "get_production_context":
        return get_production_context()
    else:
        return {"error": f"Unknown tool: {tool_name}"}