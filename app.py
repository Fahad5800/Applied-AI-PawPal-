import streamlit as st
from datetime import date
from pawpal_system import Frequency, Pet, Task, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state bootstrap
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ---------------------------------------------------------------------------
# Owner & Pet setup
# ---------------------------------------------------------------------------
st.subheader("Owner & Pet")

owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Create Owner & Pet"):
    owner = Owner(owner_name, available_hours=list(range(8, 18)))
    pet = Pet(name=pet_name, species=species, age=1)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.scheduler = Scheduler(owner)
    st.success(f"Created owner '{owner_name}' with pet '{pet_name}'.")

if st.session_state.owner:
    st.caption(f"Active owner: **{st.session_state.owner.name}** | "
               f"Pets: {[p.get_summary() for p in st.session_state.owner.pets]}")

st.divider()

# ---------------------------------------------------------------------------
# Add Task
# ---------------------------------------------------------------------------
st.subheader("Tasks")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority (1=high)", [1, 2, 3, 4, 5], index=0)
with col4:
    frequency = st.selectbox("Frequency", [f.value for f in Frequency])

if st.button("Add task"):
    if st.session_state.scheduler is None:
        st.error("Create an owner and pet first.")
    else:
        scheduler: Scheduler = st.session_state.scheduler
        pet = st.session_state.owner.pets[0]   # use first pet
        task = Task(
            task_type=task_title,
            duration=int(duration),
            priority=priority,
            frequency=Frequency(frequency),
            pet=pet,
        )
        scheduler.add_task(task)
        st.success(f"Added task: {task.get_description()}")

if st.session_state.scheduler:
    all_tasks = st.session_state.scheduler.get_pending_tasks()
    if all_tasks:
        st.write("Pending tasks:")
        st.table([{
            "id": t.id,
            "task": t.task_type,
            "pet": t.pet.name,
            "duration (min)": t.duration,
            "priority": t.priority,
            "frequency": t.frequency.value,
        } for t in all_tasks])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Generate Schedule
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.scheduler is None:
        st.error("Create an owner and pet first.")
    else:
        scheduler: Scheduler = st.session_state.scheduler
        scheduler.generate_plan(date.today())
        st.success("Schedule generated!")
        st.text(scheduler.get_plan_summary())
