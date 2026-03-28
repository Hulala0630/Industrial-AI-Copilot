import json

def get_system_state():
    with open('data/system_state.json', 'r') as f:
        data = json.load(f)
        return data