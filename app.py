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
if "sorted_tasks" not in st.session_state:
    st.session_state.sorted_tasks = []
if "unscheduled" not in st.session_state:
    st.session_state.unscheduled = []
if "overlap_conflicts" not in st.session_state:
    st.session_state.overlap_conflicts = []
if "suggested_tasks" not in st.session_state:
    st.session_state.suggested_tasks = []
if "editing_task_id" not in st.session_state:
    st.session_state.editing_task_id = None

# ---------------------------------------------------------------------------
# Owner & Pet setup
# ---------------------------------------------------------------------------
st.subheader("Owner & Pet")

owner_name = st.text_input("Owner name", value="Jordan")

if st.button("Create Owner"):
    owner = Owner(owner_name, available_hours=list(range(8, 18)))
    st.session_state.owner = owner
    st.session_state.scheduler = Scheduler(owner)
    st.success(f"Owner **{owner_name}** created!")

if st.session_state.owner:
    st.write("**Add a pet:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=30, value=1)

    if st.button("Add Pet"):
        pet = Pet(name=pet_name, species=species, age=age)
        st.session_state.owner.add_pet(pet)
        st.success(f"Pet **{pet_name}** ({species}, age {age}) added!")

if st.session_state.owner:
    owner = st.session_state.owner
    pets = owner.pets
    cols = st.columns(len(pets) + 1)
    with cols[0]:
        st.metric("Owner", owner.name)
    for i, p in enumerate(pets):
        with cols[i + 1]:
            st.info(f"🐾 {p.get_summary()}")

st.divider()

# ---------------------------------------------------------------------------
# Add Task
# ---------------------------------------------------------------------------
st.subheader("Add a Task")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority (1=high)", [1, 2, 3, 4, 5], index=0)
with col4:
    frequency = st.selectbox("Frequency", [f.value for f in Frequency])
with col5:
    if st.session_state.owner and st.session_state.owner.pets:
        pet_names = [p.name for p in st.session_state.owner.pets]
        selected_pet_for_task = st.selectbox("Pet", pet_names, key="selected_pet_for_task")
    else:
        st.selectbox("Pet", ["No pets yet"], disabled=True)

if st.button("Add task"):
    if st.session_state.scheduler is None:
        st.error("Create an owner and pet first.")
    elif not st.session_state.owner.pets:
        st.error("Add at least one pet first.")
    else:
        scheduler: Scheduler = st.session_state.scheduler
        pet_names = [p.name for p in st.session_state.owner.pets]
        selected_pet_name = st.session_state.get("selected_pet_for_task", pet_names[0])
        pet = st.session_state.owner.get_pet(selected_pet_name)
        task = Task(
            task_type=task_title,
            duration=int(duration),
            priority=priority,
            frequency=Frequency(frequency),
            pet=pet,
        )
        scheduler.add_task(task)
        st.success(f"Task **{task_title}** added for **{pet.name}** — {duration} min, priority {priority}, {frequency}.")
st.divider()

# ---------------------------------------------------------------------------
# Pending tasks
# ---------------------------------------------------------------------------
st.subheader("Pending Tasks")

PRIORITY_LABEL = {1: "🔴 High", 2: "🟠 Medium-High", 3: "🟡 Medium", 4: "🟢 Low", 5: "⚪ Minimal"}

if st.session_state.scheduler:
    scheduler: Scheduler = st.session_state.scheduler
    pending = [t for t in scheduler.filter_tasks(completed=False) if t.is_due_today()]

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

        st.write("**Manage tasks:**")
        task_options = {f"{t.task_type} ({t.pet.name})": t for t in pending_sorted}
        selected_task_name = st.selectbox(
            "Select a task", 
            list(task_options.keys()),
            key="manage_task_select"
        )
        selected_task = task_options[selected_task_name]

        col_edit, col_delete = st.columns(2)
        with col_edit:
            if st.button("✏️ Edit Task"):
                st.session_state.editing_task_id = selected_task.id

        with col_delete:
            if st.button("🗑️ Delete Task"):
                st.session_state.scheduler.remove_task(selected_task.id)
                st.success(f"Task **{selected_task_name}** deleted!")
                st.rerun()

        # --- Edit form ---
        if st.session_state.get("editing_task_id") == selected_task.id:
            st.write("**Edit task details:**")
            with st.form("edit_task_form"):
                new_title = st.text_input("Task title", value=selected_task.task_type)
                new_duration = st.number_input(
                    "Duration (min)", 
                    min_value=1, max_value=240, 
                    value=selected_task.duration
                )
                new_priority = st.selectbox(
                    "Priority (1=high)", 
                    [1, 2, 3, 4, 5],
                    index=selected_task.priority - 1
                )
                new_frequency = st.selectbox(
                    "Frequency",
                    [f.value for f in Frequency],
                    index=[f.value for f in Frequency].index(selected_task.frequency.value)
                )
                submitted = st.form_submit_button("💾 Save Changes")

                if submitted:
                    selected_task.edit_details(
                        task_type=new_title,
                        duration=new_duration,
                        priority=new_priority,
                        frequency=Frequency(new_frequency)
                    )
                    if new_duration != selected_task.duration:
                        st.warning("Duration changed — regenerate schedule to reflect new timing.")
                    st.session_state.editing_task_id = None
                    st.success(f"Task updated successfully!")
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
        st.session_state.sorted_tasks = scheduler.get_tasks_sorted_by_time()
        st.session_state.unscheduled = [
            t for t in scheduler.owner.get_all_tasks()
            if t.scheduled_time is None and not t.completed and t.is_due_today()
        ]
        st.session_state.overlap_conflicts = [
            c for c in scheduler.conflicts if c.get("type") == "time_overlap"
        ]

# --- Display schedule (outside button block so it persists) ---
if st.session_state.sorted_tasks:
    scheduler: Scheduler = st.session_state.scheduler
    sorted_tasks = st.session_state.sorted_tasks
    unscheduled = st.session_state.get("unscheduled", [])
    overlap_conflicts = st.session_state.get("overlap_conflicts", [])

    col_sched, col_unsched, col_conflicts = st.columns(3)
    col_sched.metric("Scheduled", len(sorted_tasks))
    col_unsched.metric("Unscheduled", len(unscheduled))
    col_conflicts.metric("Conflicts", len(overlap_conflicts) + len(unscheduled))

    st.success(f"Schedule generated — {len(sorted_tasks)} task(s) placed for today.")
    st.write("**Today's schedule (sorted by time):**")

    schedule_rows = [{
        "Status": "✅ Done" if t.completed else "⏳ Pending",
        "Time": t.scheduled_time.strftime("%I:%M %p") if t.scheduled_time else "—",
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
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Time": st.column_config.TextColumn("Time", width="small"),
            "Task": st.column_config.TextColumn("Task", width="large"),
            "Duration (min)": st.column_config.NumberColumn("Duration (min)", format="%d min"),
            "Priority": st.column_config.TextColumn("Priority", width="medium"),
        },
    )

    # --- Mark Task Complete ---
    st.write("**Mark a task as complete:**")
    pending_scheduled = [t for t in sorted_tasks if not t.completed]

    if pending_scheduled:
        complete_options = {
            f"{t.task_type} ({t.pet.name})": t.id
            for t in pending_scheduled
        }
        selected_to_complete = st.selectbox(
            "Select completed task",
            list(complete_options.keys()),
            key="complete_task_select"
        )
        if st.button("✅ Mark Complete"):
            task_id = complete_options[selected_to_complete]
            st.session_state.scheduler.mark_task_complete(task_id)
            # Refresh sorted_tasks to reflect completion
            st.session_state.sorted_tasks = [
                t for t in st.session_state.sorted_tasks 
                if t.id != task_id
            ]
            st.success(f"**{selected_to_complete}** marked as complete!")
            st.rerun()
    else:
        st.success("🎉 All tasks completed for today!")

    if unscheduled:
        st.warning(f"{len(unscheduled)} task(s) could not fit into available time slots.")
        with st.expander("View unscheduled tasks"):
            for t in unscheduled:
                st.error(t.get_description())

    if overlap_conflicts:
        st.error(f"{len(overlap_conflicts)} time overlap(s) detected in the schedule.")
        with st.expander("View overlap details"):
            for c in overlap_conflicts:
                st.warning(f"**{c['task1']}** overlaps **{c['task2']}**")
                st.caption(c["time"])
    elif not unscheduled:
        st.success("No conflicts detected — all tasks fit cleanly.")

    with st.expander("View raw schedule summary"):
        st.text(scheduler.get_plan_summary())
st.divider()

# ---------------------------------------------------------------------------
# AI Advisor
# ---------------------------------------------------------------------------
st.subheader("🤖 AI Pet Care Advisor")
if st.session_state.owner is None or not st.session_state.owner.pets:
    st.info("Create an owner and add at least one pet to use the AI Advisor.")
else:
    owner = st.session_state.owner
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox(
        "Select pet to ask about",
        pet_names,
        key="ai_advisor_pet"
    )
    pet = owner.get_pet(selected_pet_name)

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

    suggest_pet_name = st.selectbox(
        "Select pet to suggest tasks for",
        pet_names,
        key="suggest_pet_select"
    )
    suggest_pet = owner.get_pet(suggest_pet_name)

    if "suggested_tasks" not in st.session_state:
        st.session_state.suggested_tasks = []

    if st.button("Suggest Tasks with AI"):
        with st.spinner("Generating task suggestions..."):
            result = suggest_tasks(suggest_pet.name, suggest_pet.species, suggest_pet.age)
        if result["success"] and result["tasks"]:
            st.session_state.suggested_tasks = result["tasks"]
        else:
            st.error("Could not generate suggestions right now. Please try again shortly.")

    if st.session_state.suggested_tasks:
        st.success(f"Here are {len(st.session_state.suggested_tasks)} suggested tasks for {suggest_pet.name}:")

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
                    pet=suggest_pet,
                )
                scheduler.add_task(task)
            st.session_state.suggested_tasks = []
            st.success("All suggested tasks added!")