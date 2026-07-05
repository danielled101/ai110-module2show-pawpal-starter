from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import List, Optional


class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    ONCE = "once"


# How far out the next occurrence of a recurring task gets scheduled.
RECURRENCE_INTERVALS = {
    Frequency.DAILY: timedelta(days=1),
    Frequency.WEEKLY: timedelta(days=7),
}


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
    time: str = "00:00"  # scheduled time of day, "HH:MM" (24-hour, zero-padded)
    completed: bool = False
    due_date: Optional[date] = None  # date this instance is/was due; None = due immediately

    def mark_completed(self) -> Optional["Task"]:
        """Mark this task as done and compute its next occurrence, if any.

        DAILY and WEEKLY tasks recur, so this returns a fresh, pending
        instance representing the next occurrence (same description,
        duration, priority, and time), due one day/week after this
        instance's due date.

        Returns:
            A new pending Task for the next occurrence, or None if this
            task's frequency is ONCE (which doesn't recur).
        """
        self.completed = True
        interval = RECURRENCE_INTERVALS.get(self.frequency)
        if interval is None:
            return None
        base_date = self.due_date or date.today()
        return Task(
            description=self.description,
            duration_minutes=self.duration_minutes,
            frequency=self.frequency,
            priority=self.priority,
            time=self.time,
            due_date=base_date + interval,
        )


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

    def generate_plan(self, pet: Pet, today: Optional[date] = None) -> List[Task]:
        """Filter, sort, and return a conflict-free daily task list for a pet.

        Args:
            pet: The pet to build today's plan for.
            today: The date to treat as "today" when deciding which
                tasks are due. Defaults to the real current date.

        Returns:
            The pet's pending, due tasks in chronological order, with
            any tasks that would blow the daily time budget removed.
        """
        filtered = self.filter_tasks(pet.get_tasks(), completed=False, today=today)
        sorted_tasks = self.sort_by_time(filtered)
        conflicts = self.detect_conflicts(sorted_tasks)
        conflict_ids = {id(t) for t in conflicts}
        return [t for t in sorted_tasks if id(t) not in conflict_ids]

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks chronologically by their scheduled "HH:MM" time.

        Args:
            tasks: The tasks to sort.

        Returns:
            A new list of the same tasks ordered by `time`, tie-broken
            by priority (HIGH first).
        """
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(tasks, key=lambda t: (t.time, priority_order[t.priority]))

    def filter_tasks(
        self,
        tasks: Optional[List[Task]] = None,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
        today: Optional[date] = None,
    ) -> List[Task]:
        """Return tasks matching the given completion status and/or pet name.

        Args:
            tasks: The tasks to filter. If omitted, searches across all
                of this scheduler's owner's pets (optionally narrowed
                to one pet via `pet_name`). If given, it is filtered
                as-is and `pet_name` is ignored.
            completed: If given, keep only tasks whose `completed` flag
                matches this value.
            pet_name: If given (and `tasks` is omitted), keep only
                tasks belonging to the pet with this name.
            today: The date to treat as "today" when checking due
                dates. Defaults to the real current date.

        Returns:
            The filtered list of tasks. Tasks with a `due_date` in the
            future (relative to `today`) are always excluded — this is
            what keeps a recurring task's next occurrence from showing
            up before it's due.
        """
        if tasks is None:
            tasks = [
                t
                for pet in self.owner.pets
                if pet_name is None or pet.name == pet_name
                for t in pet.get_tasks()
            ]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if today is None:
            today = date.today()
        tasks = [t for t in tasks if t.due_date is None or t.due_date <= today]
        return tasks

    def complete_task(self, pet: Pet, task: Task) -> Optional[Task]:
        """Mark `task` complete and automatically schedule its recurrence.

        Args:
            pet: The pet `task` belongs to. If the task recurs, its
                next occurrence is appended here via `pet.add_task()`.
            task: The task to mark complete.

        Returns:
            The newly created next-occurrence Task, or None if `task`
            is a ONCE task (which doesn't recur).
        """
        next_task = task.mark_completed()
        if next_task is not None:
            pet.add_task(next_task)
        return next_task

    def detect_conflicts(self, scheduled: List[Task]) -> List[Task]:
        """Return tasks that would push the total duration over the daily time budget.

        Tasks are considered in the given order. A task only counts toward
        the running total if it fits within what's left of the budget, so
        one oversized task doesn't cause every task after it to be flagged
        too — a smaller task later in the list can still fit.

        Args:
            scheduled: The tasks to check, in the order they'd run.

        Returns:
            The tasks that don't fit within `max_daily_minutes`.
        """
        conflicts = []
        total = 0
        for task in scheduled:
            if total + task.duration_minutes > self.max_daily_minutes:
                conflicts.append(task)
            else:
                total += task.duration_minutes
        return conflicts

    def detect_time_conflicts(self, today: Optional[date] = None) -> List[str]:
        """Detect tasks (across every pet) scheduled at the same clock time.

        Groups today's pending tasks by their `time` field in a single pass
        (a dict keyed by time slot) instead of comparing every pair of tasks,
        so this stays cheap even as the number of tasks grows. Any time slot
        with more than one task — whether for the same pet or different pets
        — is a conflict. Rather than raising an exception, this returns a
        list of human-readable warning strings; the caller decides what to
        do with them (display, log, ignore).

        Args:
            today: The date to treat as "today" when deciding which
                tasks are due. Defaults to the real current date.

        Returns:
            A list of warning strings, one per conflicting time slot.
            Empty if there are no conflicts.
        """
        by_time: dict = {}
        for pet in self.owner.pets:
            pending = self.filter_tasks(pet.get_tasks(), completed=False, today=today)
            for task in pending:
                by_time.setdefault(task.time, []).append((pet, task))

        warnings = []
        for time_slot, entries in by_time.items():
            if len(entries) > 1:
                names = ", ".join(f"{task.description} ({pet.name})" for pet, task in entries)
                warnings.append(f"Time conflict at {time_slot}: {names}")
        return warnings
