from typing import Any, Dict, List
from data.data_provider.base_provider import FactoryDataProvider


class MockFactoryDataProvider(FactoryDataProvider):
    def get_system_state(self) -> Dict[str, Any]:
        return {
            "line_id": "LINE-01",
            "mode": "Auto",
            "running": False,
            "conveyor": {
                "running": False,
                "speed_mps": 0.0,
                "entry_sensor_blocked": True,
                "exit_sensor_blocked": False,
                "motor_temperature_c": 62.5
            },
            "robot": {
                "connected": True,
                "running": False,
                "fault": False,
                "program": "PickAndPlace_A"
            },
            "buffer": {
                "occupancy": 9,
                "capacity": 10
            }
        }

    def get_active_alarms(self) -> List[Dict[str, Any]]:
        return [
            {
                "alarm_id": "A001",
                "name": "Conveyor Jam",
                "severity": "High",
                "possible_cause": "Conveyor not running while entry sensor is blocked."
            }
        ]

    def get_production_context(self) -> Dict[str, Any]:
        return {
            "shift": "Night",
            "responsible_person": "Alex",
            "team": "Line Operations",
            "current_order": "PO-2026-0142",
            "product": "Battery Module",
            "target_output": 1200,
            "actual_output": 1034
        }