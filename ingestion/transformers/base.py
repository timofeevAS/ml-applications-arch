from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class Transformer(ABC):
    @abstractmethod
    def transform(self) -> dict:
        pass

@dataclass(slots=True)
class Measurment:
    sensor_id: str
    timestamp: datetime
    value: float | int | None
    value_metadata: dict[str, Any] = field(default_factory=dict)
