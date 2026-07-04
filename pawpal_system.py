from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    description: str
    duration_minutes: int
    frequency: str        # e.g. "daily", "weekly", "once"
    priority: str         # e.g. "high", "medium", "low"
    completed: bool = False

    def mark_completed(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    breed: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, _task: Task) -> None:
        pass

    def remove_task(self, _task: Task) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass


class Owner:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, _pet: Pet) -> None:
        pass

    def remove_pet(self, _pet: Pet) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def sort_by_time(self) -> List[Task]:
        pass

    def filter_tasks(self) -> List[Task]:
        pass

    def detect_conflicts(self) -> List[Task]:
        pass
