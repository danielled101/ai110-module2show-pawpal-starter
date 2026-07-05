from pawpal_system import Frequency, Pet, Priority, Task


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
