from abc import ABC, abstractmethod

class Source(ABC):
    @abstractmethod
    def fetch(self) -> dict:
        pass