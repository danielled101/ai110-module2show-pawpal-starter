import streamlit as st
from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Session state: initialize once, persist across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None

# --- Step 1: Owner & Pet ---
st.subheader("Owner & Pet Info")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Save Owner & Pet"):
    owner = Owner(name=owner_name)
    pet = Pet(name=pet_name, breed=species, age=0)
    owner.add_pet(pet)                       # Owner.add_pet() stores the pet
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.success(f"Saved {pet_name} for {owner_name}!")

st.divider()

# --- Step 2: Add Tasks ---
st.subheader("Tasks")
st.caption("Add tasks for your pet. These feed directly into the scheduler.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["high", "medium", "low"])
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

if st.button("Add task"):
    if st.session_state.pet is None:
        st.warning("Save an owner and pet first.")
    else:
        task = Task(
            description=task_title,
            duration_minutes=int(duration),
            priority=Priority(priority),      # str → Priority enum
            frequency=Frequency(frequency),   # str → Frequency enum
        )
        st.session_state.pet.add_task(task)  # Pet.add_task() stores the task
        st.success(f"Added '{task_title}' to {st.session_state.pet.name}'s tasks.")

# Show current task list
if st.session_state.pet and st.session_state.pet.get_tasks():
    st.write(f"Current tasks for **{st.session_state.pet.name}**:")
    st.table([
        {
            "Task": t.description,
            "Duration (min)": t.duration_minutes,
            "Priority": t.priority.value,
            "Frequency": t.frequency.value,
            "Done": t.completed,
        }
        for t in st.session_state.pet.get_tasks()
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Step 3: Generate Schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None or st.session_state.pet is None:
        st.warning("Save an owner and pet first.")
    elif not st.session_state.pet.get_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        plan = scheduler.generate_plan(st.session_state.pet)  # Scheduler.generate_plan()

        st.success(f"Today's plan for {st.session_state.pet.name}:")
        for task in plan:
            st.markdown(
                f"- **[{task.priority.value.upper()}]** {task.description} "
                f"— {task.duration_minutes} min ({task.frequency.value})"
            )
        total = sum(t.duration_minutes for t in plan)
        st.caption(f"Total scheduled time: {total} min")
