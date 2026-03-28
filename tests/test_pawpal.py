import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Pet, Task, Frequency, Owner, Scheduler


def make_pet():
    return Pet(name="Buddy", species="Dog", age=3)


def make_task(pet):
    return Task(
        task_type="Morning Walk",
        duration=30,
        priority=1,
        frequency=Frequency.DAILY,
        pet=pet,
    )


def test_mark_complete_changes_status():
    pet = make_pet()
    task = make_task(pet)

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = make_pet()
    assert len(pet.tasks) == 0

    task = make_task(pet)
    pet.add_task(task)
    assert len(pet.tasks) == 1

    pet.add_task(make_task(pet))
    assert len(pet.tasks) == 2


def test_filter_tasks_by_pet_and_status():
    pet = make_pet()
    other = Pet(name="Bunny", species="Rabbit", age=2)
    t1 = make_task(pet)
    t2 = Task(task_type="Vet Visit", duration=45, priority=3, frequency=Frequency.WEEKLY, pet=other)
    t2.mark_complete()

    owner = None
    from pawpal_system import Owner, Scheduler
    owner = Owner(name="Test", available_hours=[8, 9, 10])
    owner.add_pet(pet)
    owner.add_pet(other)
    sched = Scheduler(owner)
    sched.add_task(t1)
    sched.add_task(t2)

    assert len(sched.filter_tasks(pet_name="Buddy")) == 1
    assert len(sched.filter_tasks(completed=False)) == 1
    assert len(sched.filter_tasks(completed=True)) == 1


def test_generate_plan_conflict_when_insufficient_hours():
    owner = Owner(name="Test", available_hours=[8])
    pet = make_pet()
    owner.add_pet(pet)
    sched = Scheduler(owner)

    # two tasks requiring more than 60 minutes total during a single available hour
    sched.add_task(Task(task_type="Long Task A", duration=40, priority=1, frequency=Frequency.DAILY, pet=pet))
    sched.add_task(Task(task_type="Long Task B", duration=40, priority=2, frequency=Frequency.DAILY, pet=pet))

    sched.generate_plan(date.today())

    assert len(sched.conflicts) == 1
    assert sched.conflicts[0]["task_type"] == "Long Task B"


def test_get_tasks_sorted_by_time():
    owner = Owner(name="Test", available_hours=[8, 9])
    pet = make_pet()
    owner.add_pet(pet)
    sched = Scheduler(owner)

    sched.add_task(Task(task_type="A", duration=30, priority=2, frequency=Frequency.DAILY, pet=pet))
    sched.add_task(Task(task_type="B", duration=30, priority=1, frequency=Frequency.DAILY, pet=pet))
    sched.generate_plan(date.today())

    sorted_tasks = sched.get_tasks_sorted_by_time(date.today())
    assert [t.task_type for t in sorted_tasks] == ["B", "A"]


def test_detect_time_conflicts():
    owner = Owner(name="Test", available_hours=[8, 9, 10])
    pet = make_pet()
    owner.add_pet(pet)
    sched = Scheduler(owner)

    # Create tasks that will overlap when scheduled
    t1 = Task(task_type="Task A", duration=30, priority=1, frequency=Frequency.DAILY, pet=pet)
    t2 = Task(task_type="Task B", duration=30, priority=2, frequency=Frequency.DAILY, pet=pet)
    sched.add_task(t1)
    sched.add_task(t2)

    # Manually set overlapping times to test detection
    from datetime import time
    t1.scheduled_time = time(9, 0)  # 9:00 - 9:30
    t2.scheduled_time = time(9, 15)  # 9:15 - 9:45, overlaps

    conflicts = sched.detect_time_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0]["type"] == "time_overlap"
    assert "Task A" in conflicts[0]["task1"]
    assert "Task B" in conflicts[0]["task2"]


def test_recurring_task_auto_renew_on_complete():
    owner = Owner(name="Test", available_hours=[8, 9])
    pet = make_pet()
    owner.add_pet(pet)
    sched = Scheduler(owner)

    recurring = Task(task_type="Daily Walk", duration=20, priority=1, frequency=Frequency.DAILY, pet=pet)
    sched.add_task(recurring)

    sched.generate_plan(date.today())
    sched.mark_task_complete(recurring.id)

    assert recurring.completed is False  # Reset after reschedule
    assert recurring.start_date == date.today() + timedelta(days=1)
    assert len(pet.tasks) == 1  # Same task instance, not new one


if __name__ == "__main__":
    test_mark_complete_changes_status()
    print("PASS  test_mark_complete_changes_status")

    test_add_task_increases_pet_task_count()
    print("PASS  test_add_task_increases_pet_task_count")
