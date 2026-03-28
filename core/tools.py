import json

def get_system_state():
    with open('data/system_state.json', 'r') as f:
        data = json.load(f)
        return data
    
def get_alarm_rules():
    with open('data/alarms.json', 'r') as f:
        data = json.load(f)
        return data
    
def is_trigger_matched(trigger, system_state):
    #  dict trigger example: {"conveyor_running": false, "sensor_blocked": true}
    for key, expected_value in trigger.items():
        actual_value = system_state.get(key)
        if actual_value != expected_value:
            return False
    return True

def get_active_alarms():
    system_state = get_system_state()
    alarm_rules = get_alarm_rules()

    active_alarms = []

    for alarm in alarm_rules:
        if is_trigger_matched(alarm['trigger'], system_state):
            active_alarms.append(alarm)

    return active_alarms