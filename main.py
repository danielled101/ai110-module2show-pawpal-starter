from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

# --- Setup ---
owner = Owner(name="Sarah")

biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
luna = Pet(name="Luna", breed="Tabby Cat", age=5)

# --- Biscuit's tasks (added out of chronological order, on purpose) ---
biscuit.add_task(Task("Evening walk",   20, Frequency.DAILY,  Priority.MEDIUM, time="18:00"))
biscuit.add_task(Task("Morning walk",   30, Frequency.DAILY,  Priority.HIGH,   time="08:00"))
biscuit_feeding = Task("Feeding",       10, Frequency.DAILY,  Priority.HIGH,   time="07:30")
biscuit_feeding.mark_completed()  # already done today — should get filtered out below
biscuit.add_task(biscuit_feeding)

# --- Luna's tasks (added out of chronological order, on purpose) ---
luna.add_task(Task("Playtime",          15, Frequency.WEEKLY, Priority.LOW,    time="17:00"))
# Deliberately clashes with Biscuit's "Morning walk" (08:00) to demonstrate a
# cross-pet time conflict — Sarah can't walk Biscuit and medicate Luna at once.
luna.add_task(Task("Medication",         5, Frequency.DAILY,  Priority.HIGH,   time="08:00"))
luna.add_task(Task("Feeding",           10, Frequency.DAILY,  Priority.HIGH,   time="07:45"))

owner.add_pet(biscuit)
owner.add_pet(luna)

# --- Generate schedules ---
scheduler = Scheduler(owner)

print("=" * 40)
print("       Today's Schedule")
print("=" * 40)

for pet in owner.pets:
    # Filter out completed tasks, then sort the rest chronologically —
    # tasks were added out of order above, so this proves both methods work.
    pending = scheduler.filter_tasks(pet.get_tasks(), completed=False)
    ordered = scheduler.sort_by_time(pending)

    print(f"\n{pet.name} ({pet.breed})")
    print("-" * 30)
    if not ordered:
        print("  No tasks scheduled today.")
    else:
        for task in ordered:
            print(f"  {task.time} [{task.priority.value.upper()}] {task.description} — {task.duration_minutes} min ({task.frequency.value})")

print("\n" + "=" * 40)

# --- Demonstrate filter_tasks() across all pets ---
print("\nAlready completed today:")
for task in scheduler.filter_tasks(completed=True):
    print(f"  - {task.description}")

print("\nLuna's tasks only (filter by pet name):")
for task in scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna")):
    print(f"  - {task.time} {task.description}")

# --- Demonstrate detect_time_conflicts() ---
print("\nSchedule conflict check:")
conflict_warnings = scheduler.detect_time_conflicts()
if not conflict_warnings:
    print("  No conflicts detected.")
else:
    for warning in conflict_warnings:
        print(f"  WARNING: {warning}")
