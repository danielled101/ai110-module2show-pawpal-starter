from datetime import date, timedelta

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def test_mark_completed_changes_status():
    task = Task(
        description="Morning walk",
        duration_minutes=30,
        frequency=Frequency.DAILY,
        priority=Priority.HIGH,
    )
    assert task.completed is False
    task.mark_completed()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    task = Task(
        description="Feeding",
        duration_minutes=10,
        frequency=Frequency.DAILY,
        priority=Priority.HIGH,
    )
    assert len(pet.get_tasks()) == 0
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1


def _make_owner_with_two_pets():
    owner = Owner(name="Sarah")

    biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    biscuit.add_task(Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH, time="08:00"))
    feeding = Task("Feeding", 10, Frequency.DAILY, Priority.HIGH, time="07:30")
    feeding.mark_completed()
    biscuit.add_task(feeding)

    luna = Pet(name="Luna", breed="Tabby Cat", age=5)
    luna.add_task(Task("Playtime", 15, Frequency.WEEKLY, Priority.LOW, time="17:00"))

    owner.add_pet(biscuit)
    owner.add_pet(luna)
    return owner


def test_filter_tasks_by_completion_status():
    owner = _make_owner_with_two_pets()
    scheduler = Scheduler(owner)

    pending = scheduler.filter_tasks(completed=False)
    done = scheduler.filter_tasks(completed=True)

    assert [t.description for t in pending] == ["Morning walk", "Playtime"]
    assert [t.description for t in done] == ["Feeding"]


def test_filter_tasks_by_pet_name():
    owner = _make_owner_with_two_pets()
    scheduler = Scheduler(owner)

    luna_tasks = scheduler.filter_tasks(pet_name="Luna")

    assert [t.description for t in luna_tasks] == ["Playtime"]


def test_filter_tasks_by_pet_name_and_status():
    owner = _make_owner_with_two_pets()
    scheduler = Scheduler(owner)

    result = scheduler.filter_tasks(pet_name="Biscuit", completed=True)

    assert [t.description for t in result] == ["Feeding"]


def test_mark_completed_on_daily_task_returns_next_occurrence():
    task = Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH, time="08:00")

    next_task = task.mark_completed()

    assert task.completed is True
    assert next_task is not task
    assert next_task.completed is False
    assert next_task.description == "Morning walk"
    assert next_task.frequency == Frequency.DAILY
    assert next_task.time == "08:00"


def test_daily_task_due_date_is_one_day_later():
    today = date(2026, 1, 15)
    task = Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH, due_date=today)

    next_task = task.mark_completed()

    assert next_task.due_date == today + timedelta(days=1)


def test_daily_task_due_date_rolls_over_month_correctly():
    task = Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH, due_date=date(2026, 1, 31))

    next_task = task.mark_completed()

    assert next_task.due_date == date(2026, 2, 1)


def test_weekly_task_due_date_is_one_week_later():
    today = date(2026, 1, 15)
    task = Task("Playtime", 15, Frequency.WEEKLY, Priority.LOW, due_date=today)

    next_task = task.mark_completed()

    assert next_task.due_date == today + timedelta(days=7)


def test_mark_completed_on_weekly_task_returns_next_occurrence():
    task = Task("Playtime", 15, Frequency.WEEKLY, Priority.LOW, time="17:00")

    next_task = task.mark_completed()

    assert next_task is not None
    assert next_task.frequency == Frequency.WEEKLY
    assert next_task.completed is False


def test_next_occurrence_is_excluded_from_plan_until_due():
    today = date(2026, 1, 15)
    owner = Owner(name="Sarah")
    biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    task = Task("Feeding", 10, Frequency.DAILY, Priority.HIGH, time="07:30", due_date=today)
    biscuit.add_task(task)
    owner.add_pet(biscuit)
    scheduler = Scheduler(owner)

    scheduler.complete_task(biscuit, task)

    # Same day: the next occurrence (due tomorrow) shouldn't show up yet.
    assert scheduler.generate_plan(biscuit, today=today) == []
    # Next day: it becomes due and appears.
    plan_tomorrow = scheduler.generate_plan(biscuit, today=today + timedelta(days=1))
    assert [t.description for t in plan_tomorrow] == ["Feeding"]


def test_mark_completed_on_once_task_does_not_recur():
    task = Task("Vet visit", 60, Frequency.ONCE, Priority.HIGH, time="10:00")

    next_task = task.mark_completed()

    assert task.completed is True
    assert next_task is None


def test_scheduler_complete_task_adds_next_occurrence_to_pet():
    owner = Owner(name="Sarah")
    biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    task = Task("Feeding", 10, Frequency.DAILY, Priority.HIGH, time="07:30")
    biscuit.add_task(task)
    owner.add_pet(biscuit)
    scheduler = Scheduler(owner)

    scheduler.complete_task(biscuit, task)

    assert len(biscuit.get_tasks()) == 2
    assert task.completed is True
    new_task = biscuit.get_tasks()[1]
    assert new_task.completed is False
    assert new_task.description == "Feeding"


def test_scheduler_complete_task_does_not_duplicate_once_task():
    owner = Owner(name="Sarah")
    biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    task = Task("Vet visit", 60, Frequency.ONCE, Priority.HIGH, time="10:00")
    biscuit.add_task(task)
    owner.add_pet(biscuit)
    scheduler = Scheduler(owner)

    result = scheduler.complete_task(biscuit, task)

    assert result is None
    assert len(biscuit.get_tasks()) == 1
    assert task.completed is True


def test_detect_time_conflicts_same_pet():
    owner = Owner(name="Sarah")
    biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    biscuit.add_task(Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH, time="08:00"))
    biscuit.add_task(Task("Grooming", 20, Frequency.WEEKLY, Priority.LOW, time="08:00"))
    owner.add_pet(biscuit)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_time_conflicts(today=date(2026, 1, 15))

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Morning walk" in warnings[0] and "Grooming" in warnings[0]


def test_detect_time_conflicts_across_pets():
    owner = Owner(name="Sarah")
    biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    biscuit.add_task(Task("Feeding", 10, Frequency.DAILY, Priority.HIGH, time="07:30"))
    luna = Pet(name="Luna", breed="Tabby Cat", age=5)
    luna.add_task(Task("Feeding", 10, Frequency.DAILY, Priority.HIGH, time="07:30"))
    owner.add_pet(biscuit)
    owner.add_pet(luna)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_time_conflicts(today=date(2026, 1, 15))

    assert len(warnings) == 1
    assert "Biscuit" in warnings[0] and "Luna" in warnings[0]


def test_detect_time_conflicts_no_overlap_returns_no_warnings():
    owner = Owner(name="Sarah")
    biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    biscuit.add_task(Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH, time="08:00"))
    biscuit.add_task(Task("Evening walk", 20, Frequency.DAILY, Priority.MEDIUM, time="18:00"))
    owner.add_pet(biscuit)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_time_conflicts(today=date(2026, 1, 15))

    assert warnings == []


def test_detect_time_conflicts_ignores_completed_and_not_yet_due_tasks():
    today = date(2026, 1, 15)
    owner = Owner(name="Sarah")
    biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    # Same time slot, but one is already completed and one isn't due until tomorrow —
    # neither should actually happen today, so they shouldn't count as a conflict.
    completed_task = Task("Old feeding", 10, Frequency.DAILY, Priority.HIGH, time="08:00", due_date=today)
    completed_task.completed = True
    not_yet_due = Task("Future task", 10, Frequency.DAILY, Priority.HIGH, time="08:00", due_date=today + timedelta(days=1))
    active = Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH, time="08:00", due_date=today)
    biscuit.add_task(completed_task)
    biscuit.add_task(not_yet_due)
    biscuit.add_task(active)
    owner.add_pet(biscuit)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_time_conflicts(today=today)

    assert warnings == []
