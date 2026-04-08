from __future__ import annotations

from typing import Any, Dict, List
import pandas as pd

from data.data_provider.base_provider import FactoryDataProvider


class DatasetFactoryDataProvider(FactoryDataProvider):
    """
    Convert a tabular dataset into agent-friendly industrial semantics.

    Assumptions for the first version:
    - One row represents the latest equipment/system snapshot.
    - Required columns are mapped through `column_map`.
    - Missing columns fall back to defaults.
    """

    def __init__(self, csv_path: str, column_map: Dict[str, str] | None = None):
        self.csv_path = csv_path
        self.column_map = column_map or {}
        self.df = pd.read_csv(csv_path)

        if self.df.empty:
            raise ValueError(f"Dataset at {csv_path} is empty.")

    def _latest_row(self) -> pd.Series:
        return self.df.iloc[-1]

    def _get(self, row: pd.Series, semantic_key: str, default: Any = None) -> Any:
        col = self.column_map.get(semantic_key)
        if col and col in row.index:
            value = row[col]
            if pd.isna(value):
                return default
            return value
        return default

    def get_system_state(self) -> Dict[str, Any]:
        row = self._latest_row()

        conveyor_running = bool(self._get(row, "conveyor_running", False))
        entry_sensor_blocked = bool(self._get(row, "entry_sensor_blocked", False))
        exit_sensor_blocked = bool(self._get(row, "exit_sensor_blocked", False))
        speed_mps = float(self._get(row, "conveyor_speed_mps", 0.0))
        motor_temp = float(self._get(row, "motor_temperature_c", 0.0))

        robot_connected = bool(self._get(row, "robot_connected", True))
        robot_running = bool(self._get(row, "robot_running", False))
        robot_fault = bool(self._get(row, "robot_fault", False))

        buffer_occupancy = int(self._get(row, "buffer_occupancy", 0))
        buffer_capacity = int(self._get(row, "buffer_capacity", 10))

        return {
            "line_id": self._get(row, "line_id", "LINE-01"),
            "mode": self._get(row, "mode", "Auto"),
            "running": bool(self._get(row, "system_running", conveyor_running or robot_running)),
            "conveyor": {
                "running": conveyor_running,
                "speed_mps": speed_mps,
                "entry_sensor_blocked": entry_sensor_blocked,
                "exit_sensor_blocked": exit_sensor_blocked,
                "motor_temperature_c": motor_temp
            },
            "robot": {
                "connected": robot_connected,
                "running": robot_running,
                "fault": robot_fault,
                "program": self._get(row, "robot_program", "Unknown")
            },
            "buffer": {
                "occupancy": buffer_occupancy,
                "capacity": buffer_capacity
            }
        }

    def get_active_alarms(self) -> List[Dict[str, Any]]:
        row = self._latest_row()
        alarms: List[Dict[str, Any]] = []

       
        conveyor_running = bool(self._get(row, "conveyor_running", False))
        entry_sensor_blocked = bool(self._get(row, "entry_sensor_blocked", False))
        motor_temp = float(self._get(row, "motor_temperature_c", 0.0))
        robot_fault = bool(self._get(row, "robot_fault", False))

        if (not conveyor_running) and entry_sensor_blocked:
            alarms.append({
                "alarm_id": "A001",
                "name": "Conveyor Jam",
                "severity": "High",
                "possible_cause": "Conveyor is stopped while entry sensor is blocked."
            })

        if motor_temp >= 75.0:
            alarms.append({
                "alarm_id": "A002",
                "name": "Conveyor Motor Overheat",
                "severity": "Medium",
                "possible_cause": "Motor temperature exceeded threshold."
            })

        if robot_fault:
            alarms.append({
                "alarm_id": "A003",
                "name": "Robot Fault",
                "severity": "High",
                "possible_cause": "Robot fault flag is active."
            })

        return alarms

    def get_production_context(self) -> Dict[str, Any]:
        row = self._latest_row()

        return {
            "shift": self._get(row, "shift", "Unknown"),
            "responsible_person": self._get(row, "responsible_person", "Unknown"),
            "team": self._get(row, "team", "Unknown"),
            "current_order": self._get(row, "current_order", "Unknown"),
            "product": self._get(row, "product", "Unknown"),
            "target_output": int(self._get(row, "target_output", 0)),
            "actual_output": int(self._get(row, "actual_output", 0))
        }