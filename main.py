from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

# --- Setup ---
owner = Owner(name="Sarah")

biscuit = Pet(name="Biscuit", breed="Golden Retriever", age=3)
luna = Pet(name="Luna", breed="Tabby Cat", age=5)

# --- Biscuit's tasks ---
biscuit.add_task(Task("Morning walk",   30, Frequency.DAILY,  Priority.HIGH))
biscuit.add_task(Task("Feeding",        10, Frequency.DAILY,  Priority.HIGH))
biscuit.add_task(Task("Evening walk",   20, Frequency.DAILY,  Priority.MEDIUM))

# --- Luna's tasks ---
luna.add_task(Task("Feeding",           10, Frequency.DAILY,  Priority.HIGH))
luna.add_task(Task("Medication",         5, Frequency.DAILY,  Priority.HIGH))
luna.add_task(Task("Playtime",          15, Frequency.WEEKLY, Priority.LOW))

owner.add_pet(biscuit)
owner.add_pet(luna)

# --- Generate schedules ---
scheduler = Scheduler(owner)

print("=" * 40)
print("       Today's Schedule")
print("=" * 40)

for pet in owner.pets:
    plan = scheduler.generate_plan(pet)
    print(f"\n{pet.name} ({pet.breed})")
    print("-" * 30)
    if not plan:
        print("  No tasks scheduled today.")
    else:
        for task in plan:
            print(f"  [{task.priority.value.upper()}] {task.description} — {task.duration_minutes} min ({task.frequency.value})")

print("\n" + "=" * 40)
