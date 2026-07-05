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


def test_sort_by_time_breaks_ties_by_priority():
    scheduler = Scheduler(Owner(name="Sarah"))
    low = Task("Playtime", 15, Frequency.DAILY, Priority.LOW, time="08:00")
    high = Task("Medication", 5, Frequency.DAILY, Priority.HIGH, time="08:00")
    medium = Task("Brushing", 10, Frequency.DAILY, Priority.MEDIUM, time="08:00")

    ordered = scheduler.sort_by_time([low, medium, high])

    assert [t.description for t in ordered] == ["Medication", "Brushing", "Playtime"]


def test_detect_conflicts_does_not_cascade_after_oversized_task():
    scheduler = Scheduler(Owner(name="Sarah"), max_daily_minutes=60)
    big = Task("Long hike", 50, Frequency.DAILY, Priority.HIGH, time="08:00")
    also_big = Task("Grooming", 40, Frequency.DAILY, Priority.MEDIUM, time="09:00")
    small = Task("Feeding", 5, Frequency.DAILY, Priority.LOW, time="10:00")

    # big fits (50 <= 60). also_big doesn't fit on top of it (50+40=90 > 60), so it's
    # a conflict and its minutes are never added to the running total. small should
    # still fit (50+5=55 <= 60) even though it comes after a conflicting task.
    conflicts = scheduler.detect_conflicts([big, also_big, small])

    assert big not in conflicts
    assert also_big in conflicts
    assert small not in conflicts


def test_generate_plan_excludes_only_the_oversized_task():
    owner = Owner(name="Sarah")
    biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    biscuit.add_task(Task("Long hike", 50, Frequency.DAILY, Priority.HIGH, time="08:00"))
    biscuit.add_task(Task("Grooming", 40, Frequency.DAILY, Priority.MEDIUM, time="09:00"))
    biscuit.add_task(Task("Feeding", 5, Frequency.DAILY, Priority.LOW, time="10:00"))
    owner.add_pet(biscuit)
    scheduler = Scheduler(owner, max_daily_minutes=60)

    plan = scheduler.generate_plan(biscuit)

    assert [t.description for t in plan] == ["Long hike", "Feeding"]


def test_generate_plan_excludes_conflict_by_identity_not_value():
    owner = Owner(name="Sarah")
    biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    # Two separate task instances that happen to be equal by value (dataclass
    # equality compares fields, not identity) — only the one that doesn't fit
    # the budget should be dropped, not both.
    overflowing = Task("Feeding", 50, Frequency.DAILY, Priority.HIGH, time="08:00")
    identical_but_fits_alone = Task("Feeding", 50, Frequency.DAILY, Priority.HIGH, time="08:00")
    biscuit.add_task(overflowing)
    biscuit.add_task(identical_but_fits_alone)
    owner.add_pet(biscuit)
    scheduler = Scheduler(owner, max_daily_minutes=50)

    plan = scheduler.generate_plan(biscuit)

    assert plan == [overflowing]


# --- Sorting correctness ---


def test_sort_by_time_returns_chronological_order():
    scheduler = Scheduler(Owner(name="Sarah"))
    evening = Task("Evening walk", 20, Frequency.DAILY, Priority.MEDIUM, time="18:00")
    morning = Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH, time="08:00")
    midday = Task("Lunch", 10, Frequency.DAILY, Priority.LOW, time="12:00")

    ordered = scheduler.sort_by_time([evening, morning, midday])

    assert [t.description for t in ordered] == ["Morning walk", "Lunch", "Evening walk"]


def test_sort_by_time_and_filter_tasks_accept_empty_list():
    scheduler = Scheduler(Owner(name="Sarah"))

    assert scheduler.sort_by_time([]) == []
    assert scheduler.filter_tasks([], completed=False) == []


def test_generate_plan_is_empty_for_pet_with_no_tasks():
    owner = Owner(name="Sarah")
    pet = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    assert scheduler.generate_plan(pet) == []


# --- Recurrence logic ---


def test_completing_daily_task_schedules_it_for_tomorrow_in_generated_plan():
    today = date(2026, 3, 10)
    owner = Owner(name="Sarah")
    pet = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    task = Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH, time="08:00", due_date=today)
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    scheduler.complete_task(pet, task)

    assert scheduler.generate_plan(pet, today=today) == []
    tomorrow_plan = scheduler.generate_plan(pet, today=today + timedelta(days=1))
    assert [t.description for t in tomorrow_plan] == ["Morning walk"]


def test_recurrence_advances_due_date_across_multiple_cycles():
    today = date(2026, 3, 10)
    task = Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH, due_date=today)

    cycle_1 = task.mark_completed()
    cycle_2 = cycle_1.mark_completed()
    cycle_3 = cycle_2.mark_completed()

    assert cycle_1.due_date == today + timedelta(days=1)
    assert cycle_2.due_date == today + timedelta(days=2)
    assert cycle_3.due_date == today + timedelta(days=3)


# --- Conflict detection ---


def test_detect_time_conflicts_flags_all_tasks_sharing_a_time_slot():
    owner = Owner(name="Sarah")
    biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    luna = Pet(name="Luna", breed="Tabby Cat", age=5)
    max_pet = Pet(name="Max", breed="Beagle", age=2)
    biscuit.add_task(Task("Morning walk", 30, Frequency.DAILY, Priority.HIGH, time="08:00"))
    luna.add_task(Task("Medication", 5, Frequency.DAILY, Priority.HIGH, time="08:00"))
    max_pet.add_task(Task("Feeding", 10, Frequency.DAILY, Priority.HIGH, time="08:00"))
    owner.add_pet(biscuit)
    owner.add_pet(luna)
    owner.add_pet(max_pet)
    scheduler = Scheduler(owner)

    warnings = scheduler.detect_time_conflicts(today=date(2026, 3, 10))

    assert len(warnings) == 1
    for name in ("Morning walk", "Medication", "Feeding"):
        assert name in warnings[0]


def test_detect_conflicts_task_exactly_at_budget_limit_is_not_flagged():
    scheduler = Scheduler(Owner(name="Sarah"), max_daily_minutes=60)
    task = Task("Long hike", 60, Frequency.DAILY, Priority.HIGH, time="08:00")

    conflicts = scheduler.detect_conflicts([task])

    assert conflicts == []


# --- Other edge cases ---


def test_remove_task_removes_it_from_pets_list():
    pet = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    task = Task("Feeding", 10, Frequency.DAILY, Priority.HIGH)
    pet.add_task(task)

    pet.remove_task(task)

    assert pet.get_tasks() == []


def test_remove_pet_removes_it_from_owners_list():
    owner = Owner(name="Sarah")
    pet = Pet(name="Biscuit", breed="Golden Retriever", age=3)
    owner.add_pet(pet)

    owner.remove_pet(pet)

    assert owner.pets == []


def test_filter_tasks_by_unknown_pet_name_returns_empty_list():
    owner = _make_owner_with_two_pets()
    scheduler = Scheduler(owner)

    result = scheduler.filter_tasks(pet_name="Ghost")

    assert result == []
