from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field

from transformers.base import Measurment

class Deduplicator(ABC):
    def is_new(self, measurement: Measurment) -> bool:
        pass


@dataclass(slots=True)
class InMemoryDeduplicator(Deduplicator):
    seen_keys: set[tuple[str, str]] = field(default_factory=set)

    def is_new(self, measurement: Measurment) -> bool:
        key = (measurement.sensor_id, measurement.timestamp)

        if key in self.seen_keys:
            return False

        self.seen_keys.add(key)
        return True
    
    def clear(self) -> None:
        self.seen_keys.clear()