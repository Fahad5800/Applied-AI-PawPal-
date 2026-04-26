import streamlit as st
from datetime import date
from pawpal_system import Frequency, Pet, Task, Owner, Scheduler
from ai_advisor import ask_pet_advisor, suggest_tasks

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
    st.success(f"Owner **{owner_name}** created with pet **{pet_name}** ({species}).")

if st.session_state.owner:
    owner = st.session_state.owner
    pets = owner.pets
    cols = st.columns(len(pets) + 1)
    with cols[0]:
        st.metric("Owner", owner.name)
    for i, p in enumerate(pets):
        with cols[i + 1]:
            st.metric(f"Pet {i + 1}", p.name, f"{p.species}, age {p.age}")

st.divider()

# ---------------------------------------------------------------------------
# Add Task
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority (1=high)", [1, 2, 3, 4, 5], index=0)
with col4:
    frequency = st.selectbox("Frequency", [f.value for f in Frequency])

if st.button("Add task"):
    if st.session_state.scheduler is None:
        st.error("Create an owner and pet first.")
    else:
        scheduler: Scheduler = st.session_state.scheduler
        pet = st.session_state.owner.pets[0]
        task = Task(
            task_type=task_title,
            duration=int(duration),
            priority=priority,
            frequency=Frequency(frequency),
            pet=pet,
        )
        scheduler.add_task(task)
        st.success(f"Task **{task_title}** added — {duration} min, priority {priority}, {frequency}.")

st.divider()

# ---------------------------------------------------------------------------
# Pending tasks
# ---------------------------------------------------------------------------
st.subheader("Pending Tasks")

PRIORITY_LABEL = {1: "🔴 High", 2: "🟠 Medium-High", 3: "🟡 Medium", 4: "🟢 Low", 5: "⚪ Minimal"}

if st.session_state.scheduler:
    scheduler: Scheduler = st.session_state.scheduler
    pending = scheduler.filter_tasks(completed=False)

    if pending:
        pending_sorted = sorted(pending, key=lambda t: t.priority)

        col_total, col_high, col_today = st.columns(3)
        high_priority = [t for t in pending_sorted if t.priority == 1]
        due_today = [t for t in pending_sorted if t.is_due_today()]
        col_total.metric("Total pending", len(pending_sorted))
        col_high.metric("High priority", len(high_priority))
        col_today.metric("Due today", len(due_today))

        rows = [{
            "Priority": PRIORITY_LABEL.get(t.priority, str(t.priority)),
            "Task": t.task_type,
            "Pet": t.pet.name,
            "Duration (min)": t.duration,
            "Frequency": t.frequency.value.capitalize(),
        } for t in pending_sorted]

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Priority": st.column_config.TextColumn("Priority", width="medium"),
                "Task": st.column_config.TextColumn("Task", width="large"),
                "Duration (min)": st.column_config.NumberColumn("Duration (min)", format="%d min"),
            },
        )

        st.write("**Delete a task:**")
        task_options = {f"{t.task_type} ({t.pet.name})": t.id for t in pending_sorted}
        selected_task = st.selectbox("Select task to delete", list(task_options.keys()))
        if st.button("Delete Task"):
            task_id = task_options[selected_task]
            st.session_state.scheduler.remove_task(task_id)
            st.success(f"Task **{selected_task}** deleted!")
            st.rerun()
    else:
        st.info("No pending tasks. Add one above.")

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

        sorted_tasks = scheduler.get_tasks_sorted_by_time()
        unscheduled = [
            t for t in scheduler.owner.get_all_tasks()
            if t.scheduled_time is None and not t.completed and t.is_due_today()
        ]
        overlap_conflicts = [c for c in scheduler.conflicts if c.get("type") == "time_overlap"]

        # Summary metrics
        col_sched, col_unsched, col_conflicts = st.columns(3)
        col_sched.metric("Scheduled", len(sorted_tasks))
        col_unsched.metric("Unscheduled", len(unscheduled))
        col_conflicts.metric("Conflicts", len(overlap_conflicts) + len(unscheduled))

        if sorted_tasks:
            st.success(f"Schedule generated — {len(sorted_tasks)} task(s) placed for today.")
            st.write("**Today's schedule (sorted by time):**")
            schedule_rows = [{
                "Time": t.scheduled_time.strftime("%I:%M %p"),
                "Task": t.task_type,
                "Pet": t.pet.name,
                "Duration (min)": t.duration,
                "Priority": PRIORITY_LABEL.get(t.priority, str(t.priority)),
            } for t in sorted_tasks]

            st.dataframe(
                schedule_rows,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Time": st.column_config.TextColumn("Time", width="small"),
                    "Task": st.column_config.TextColumn("Task", width="large"),
                    "Duration (min)": st.column_config.NumberColumn("Duration (min)", format="%d min"),
                    "Priority": st.column_config.TextColumn("Priority", width="medium"),
                },
            )
        else:
            st.warning("No tasks could be scheduled for today.")

        if unscheduled:
            st.warning(f"{len(unscheduled)} task(s) could not fit into available time slots.")
            with st.expander("View unscheduled tasks"):
                for t in unscheduled:
                    st.error(
                        f"**{t.task_type}** — {t.pet.name} | {t.duration} min | priority {t.priority}"
                    )

        if overlap_conflicts:
            st.error(f"{len(overlap_conflicts)} time overlap(s) detected in the schedule.")
            with st.expander("View overlap details"):
                for c in overlap_conflicts:
                    st.warning(f"**{c['task1']}** overlaps **{c['task2']}**")
                    st.caption(c["time"])
        elif not unscheduled:
            st.success("No conflicts detected — all tasks fit cleanly.")    
st.divider()

# ---------------------------------------------------------------------------
# AI Advisor
# ---------------------------------------------------------------------------
st.subheader("🤖 AI Pet Care Advisor")

if st.session_state.owner is None:
    st.info("Create an owner and pet first to use the AI Advisor.")
else:
    owner = st.session_state.owner
    pet = owner.pets[0]

    # --- Ask a question ---
    st.write("**Ask a pet care question:**")
    question = st.text_input("Your question", value="How often should I walk my dog?")

    if st.button("Ask AI Advisor"):
        with st.spinner("Thinking..."):
            result = ask_pet_advisor(question, pet.name, pet.species, pet.age)

        if result["success"]:
            st.success(result["answer"])
            confidence = result["confidence"]
            if confidence >= 0.8:
                st.metric("Confidence Score", f"{confidence:.0%}", "High confidence")
            elif confidence >= 0.5:
                st.metric("Confidence Score", f"{confidence:.0%}", "Medium confidence")
            else:
                st.metric("Confidence Score", f"{confidence:.0%}", "Low confidence")
        else:
            st.error("AI Advisor is unavailable right now. Please try again shortly.")

    st.divider()

    # --- Suggest Tasks ---
    st.write("**Let AI suggest tasks for your pet:**")
    
    if "suggested_tasks" not in st.session_state:
        st.session_state.suggested_tasks = []

    if st.button("Suggest Tasks with AI"):
        with st.spinner("Generating task suggestions..."):
            result = suggest_tasks(pet.name, pet.species, pet.age)

        if result["success"] and result["tasks"]:
            st.session_state.suggested_tasks = result["tasks"]
        else:
            st.error("Could not generate suggestions right now. Please try again shortly.")

    if st.session_state.suggested_tasks:
        st.success(f"Here are {len(st.session_state.suggested_tasks)} suggested tasks for {pet.name}:")

        for t in st.session_state.suggested_tasks:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{t['task']}**")
            with col2:
                st.write(f"⏱ {t['duration_minutes']} min")
            with col3:
                st.write(f"📅 {t['frequency'].capitalize()}")

        if st.button("Add All Suggested Tasks"):
            scheduler = st.session_state.scheduler
            for t in st.session_state.suggested_tasks:
                task = Task(
                    task_type=t["task"],
                    duration=int(t["duration_minutes"]),
                    priority=int(t["priority"]),
                    frequency=Frequency(t["frequency"]),
                    pet=pet,
                )
                scheduler.add_task(task)
            st.session_state.suggested_tasks = []
            st.success("All suggested tasks added!")