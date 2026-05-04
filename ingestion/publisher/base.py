from abc import ABC, abstractmethod

from transformers.base import Measurment


class Publisher(ABC):
    @abstractmethod
    def publish(self, data: list[Measurment]) -> None:
        pass
