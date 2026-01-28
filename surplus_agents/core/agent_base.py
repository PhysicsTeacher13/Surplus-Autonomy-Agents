from abc import ABC, abstractmethod
from datetime import datetime

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.started_at = datetime.utcnow()

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    def log(self, message: str):
        ts = datetime.utcnow().isoformat()
        print(f"[{ts}] [{self.name}] {message}")
