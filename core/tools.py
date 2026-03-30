import json

def load_json_file(file_path):
    with open(file_path, 'r',encoding="utf-8") as f:
        return json.load(f)
 
    
def get_system_state():
    return load_json_file('data/system_state.json')
    
def get_alarm_rules():
    return load_json_file('data/alarms_rules.json')

def get_alarm_history():
    return load_json_file('data/alarm_history.json')

def get_production_context():
    return load_json_file('data/production_context.json')

def get_nested_value(data, path):
    keys = path.split(".")
    current = data
    for key in keys:
        current = current.get(key)
        if current is None:
            return None

    return current

    
def is_trigger_matched(trigger, system_state):
   
    for key, expected_value in trigger.items():
        actual_value = get_nested_value(system_state, key)
        #get the actual value based on the name of the trigger, which can be nested like "conveyor.running"
        if actual_value != expected_value:
            return False
    return True

def get_active_alarms():
    system_state = get_system_state()
    alarm_rules = get_alarm_rules()

    active_alarms = []

    for alarm in alarm_rules:
        trigger_logic = alarm["trigger_logic"]

        if is_trigger_matched(trigger_logic, system_state):
            active_alarms.append(alarm)

    return active_alarms