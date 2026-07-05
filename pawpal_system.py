from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    ONCE = "once"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    description: str
    duration_minutes: int
    frequency: Frequency
    priority: Priority
    completed: bool = False

    def mark_completed(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    name: str
    breed: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks


class Owner:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's pet list."""
        self.pets.remove(pet)


class Scheduler:
    def __init__(self, owner: Owner, max_daily_minutes: int = 480) -> None:
        self.owner = owner
        self.max_daily_minutes = max_daily_minutes

    def generate_plan(self, pet: Pet) -> List[Task]:
        """Filter, sort, and return a conflict-free daily task list for a pet."""
        filtered = self.filter_tasks(pet.get_tasks())
        sorted_tasks = self.sort_by_time(filtered)
        conflicts = self.detect_conflicts(sorted_tasks)
        return [t for t in sorted_tasks if t not in conflicts]

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (high first), then by shortest duration."""
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(tasks, key=lambda t: (order[t.priority], t.duration_minutes))

    def filter_tasks(self, tasks: List[Task]) -> List[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in tasks if not t.completed]

    def detect_conflicts(self, scheduled: List[Task]) -> List[Task]:
        """Return tasks that push the total duration over the daily time budget."""
        conflicts = []
        total = 0
        for task in scheduled:
            total += task.duration_minutes
            if total > self.max_daily_minutes:
                conflicts.append(task)
        return conflicts
