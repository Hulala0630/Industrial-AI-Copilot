tools = [
    {
        "type": "function",
        "function": {
            "name": "get_system_state",
            "description": "Use this when the user asks about current machine state, current status, current condition, or real-time operating state.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_alarms",
            "description": "Use this when the user asks about alarms, faults, causes, abnormal conditions, or troubleshooting suggestions.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_production_context",
            "description": "Use this when the user asks about shift, operator, recipe, production target, production progress, or broader production context. This tool contains the exact operator name responsible for current operation.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]