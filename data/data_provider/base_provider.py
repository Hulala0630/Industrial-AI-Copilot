
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class FactoryDataProvider(ABC):
    @abstractmethod
    def get_system_state(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_active_alarms(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_production_context(self) -> Dict[str, Any]:
        raise NotImplementedError