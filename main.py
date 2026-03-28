from datetime import date, time
from pawpal_system import Owner, Pet, Task, Scheduler, Frequency

# --- Setup ---
owner = Owner(name="Alex", available_hours=[8, 9, 10, 14, 16])

buddy = Pet(name="Buddy", species="Dog", age=3)
whiskers = Pet(name="Whiskers", species="Cat", age=5, special_needs=["indoor only"])

owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Tasks ---
scheduler = Scheduler(owner)

scheduler.add_task(Task(
    task_type="Morning Walk",
    duration=30,
    priority=1,
    frequency=Frequency.DAILY,
    pet=buddy,
))

scheduler.add_task(Task(
    task_type="Feed Breakfast",
    duration=10,
    priority=2,
    frequency=Frequency.DAILY,
    pet=buddy,
))

scheduler.add_task(Task(
    task_type="Clean Litter Box",
    duration=15,
    priority=2,
    frequency=Frequency.DAILY,
    pet=whiskers,
))

scheduler.add_task(Task(
    task_type="Vet Checkup",
    duration=60,
    priority=1,
    frequency=Frequency.MONTHLY,
    pet=whiskers,
))

# --- Add tasks in out-of-order sequence ---
scheduler.add_task(Task(task_type="Midday Groom", duration=20, priority=3, frequency=Frequency.DAILY, pet=buddy))
scheduler.add_task(Task(task_type="Evening Play", duration=30, priority=2, frequency=Frequency.DAILY, pet=whiskers))
scheduler.add_task(Task(task_type="Morning Medication", duration=10, priority=1, frequency=Frequency.DAILY, pet=whiskers))

# Add tasks with pre-set overlapping times to demonstrate conflict detection
overlapping_task1 = Task(task_type="Grooming Session", duration=45, priority=2, frequency=Frequency.WEEKLY, pet=buddy)
overlapping_task1.scheduled_time = time(10, 0)  # 10:00 - 10:45
scheduler.add_task(overlapping_task1)

overlapping_task2 = Task(task_type="Training Session", duration=30, priority=3, frequency=Frequency.DAILY, pet=buddy)
overlapping_task2.scheduled_time = time(10, 15)  # 10:15 - 10:45, overlaps with grooming
scheduler.add_task(overlapping_task2)

# --- Generate and print today's schedule ---
today = date.today()
scheduler.generate_plan(today)

print("=" * 50)
print(f"  PawPal+ | Today's Schedule ({today})")
print("=" * 50)

print("\nPets:")
for pet in owner.pets:
    print(f"  {pet.get_summary()}")

print()
print("Unsorted tasks (due today, as loaded):")
for task in owner.get_all_tasks():
    print(f"  {task.get_description()}")

print()
print("Sorted by time:")
for task in scheduler.sort_by_time():
    print(f"  {task.get_description()}")

print()
print("Filtered tasks (pet=Whiskers):")
for task in scheduler.filter_tasks(pet_name="Whiskers"):
    print(f"  {task.get_description()}")

print()
# mark one task as complete to test status filter
morning_med = [t for t in owner.get_all_tasks() if t.task_type == "Morning Medication"][0]
morning_med.mark_complete()

print("Filtered tasks (completed=true):")
for task in scheduler.filter_tasks(completed=True):
    print(f"  {task.get_description()}")

print()
# Demonstrate recurring task reschedule
print("Before marking daily walk complete:")
daily_walk = [t for t in owner.get_all_tasks() if t.task_type == "Morning Walk"][0]
print(f"  {daily_walk.get_description()}")

scheduler.mark_task_complete(daily_walk.id)

print("After marking daily walk complete (rescheduled):")
print(f"  {daily_walk.get_description()}")

print("\nFiltered tasks (completed=false):")
for task in scheduler.filter_tasks(completed=False):
    print(f"  {task.get_description()}")

print("\nSchedule Summary:")
print(scheduler.get_plan_summary())

# Now manually set two tasks to the same time to demonstrate conflict detection
grooming = [t for t in owner.get_all_tasks() if t.task_type == "Grooming Session"][0]
training = [t for t in owner.get_all_tasks() if t.task_type == "Training Session"][0]
grooming.scheduled_time = time(14, 0)  # 2:00 PM - 2:45 PM
training.scheduled_time = time(14, 30)  # 2:30 PM - 3:00 PM, overlaps

print("\nAfter manually setting overlapping times for Grooming and Training:")
time_conflicts = scheduler.detect_time_conflicts()
if time_conflicts:
    print("Time conflicts detected:")
    for conflict in time_conflicts:
        print(f"  - {conflict['task1']} and {conflict['task2']} ({conflict['time']})")
else:
    print("No time conflicts.")

print("=" * 50)
