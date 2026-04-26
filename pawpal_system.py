from dataclasses import dataclass, field
from datetime import date, time, timedelta, datetime
import logging
from typing import List, Dict, Any, Optional
from enum import Enum

# WarningLevel: Three labels: INFO, WARNING, and CRITICAL.
class WarningLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

# ConflictLogger: A safety net, it records the probelems.
class ConflictLogger:
    """Lightweight conflict logging that returns warnings instead of crashing."""
    
    def __init__(self, log_file: str = "pawpal_conflicts.log"):
        """Initialize the conflict logger.
        
        Args:
            log_file (str): Path to the log file (default: "pawpal_conflicts.log").
        """
        self.log_file = log_file
        self.warnings = []
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging configuration for console warnings."""
        self.logger = logging.getLogger("PawPal.Scheduler")
        self.logger.setLevel(logging.WARNING)
        
        # Console handler with simple formatting
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        formatter = logging.Formatter('⚠️  [%(levelname)s] %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
    
    def log_warning(self, message: str, level: WarningLevel = WarningLevel.WARNING, metadata=None):
        """Log a warning message with optional metadata without stopping execution.
        
        Args:
            message (str): The warning message to log.
            level (WarningLevel): Severity level of the warning.
            metadata (dict): Optional additional data for the warning.
        """
        warning_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "message": message,
            "metadata": metadata or {}
        }
        self.warnings.append(warning_data)
        
        if level == WarningLevel.CRITICAL:
            self.logger.critical(message)
        elif level == WarningLevel.WARNING:
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def get_warning_summary(self) -> str:
        """Return a summary string of logged warnings.
        
        Returns:
            str: Summary of warnings or success message.
        """
        if not self.warnings:
            return "✓ No conflicts detected."
        return f"⚠️  ({len(self.warnings)} warnings logged)"

# ENUM: 3 labels: DAILY, WEEKLY, and MONTHLY.
class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

# stores pet profiles and list of tasks.
@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: List[str] = field(default_factory=list)
    tasks: List["Task"] = field(default_factory=list)

    def add_task(self, task: "Task"):
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: int):
        """Remove the task with the given id from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_summary(self) -> str:
        """Return a single-line string summarising the pet's key details."""
        needs = ", ".join(self.special_needs) if self.special_needs else "none"
        return (
            f"{self.name} ({self.species}, age {self.age})"
        )


_task_id_counter = iter(range(1, 10_000))

# Taks class that handles scheduling, importance of task, it's due dates etc. 
@dataclass
class Task:
    task_type: str
    duration: int          # minutes
    priority: int          # 1 (highest) – 5 (lowest)
    frequency: Frequency
    pet: Pet
    start_date: date = field(default_factory=date.today)
    scheduled_time: Optional[time] = None
    completed: bool = False
    id: int = field(default_factory=lambda: next(_task_id_counter))

    def is_due_on(self, check_date: date) -> bool:
        """Return True if this task should occur on check_date."""
        if check_date < self.start_date:
            return False

        if self.frequency == Frequency.DAILY:
            return True
        if self.frequency == Frequency.WEEKLY:
            return check_date.weekday() == self.start_date.weekday()
        if self.frequency == Frequency.MONTHLY:
            return check_date.day == self.start_date.day
        return False

    def is_due_today(self) -> bool:
        """Return True if this task is due on today's date."""
        return self.is_due_on(date.today())

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def edit_details(self, task_type: str, duration: int, priority: int, frequency: Frequency):
        """Update the task's core attributes in place."""
        self.task_type = task_type
        self.duration = duration
        self.priority = priority
        self.frequency = frequency

    def get_next_due_date(self) -> date:
        """Calculate the next due date based on frequency.
        
        Computes the next occurrence date for recurring tasks:
        - DAILY: Tomorrow
        - WEEKLY: Next occurrence of the same weekday as start_date
        - MONTHLY: Same day next month, handling month-end edge cases
        
        Returns:
            date: The next due date.
        """
        today = date.today()

        if self.frequency == Frequency.DAILY:
            return today + timedelta(days=1)
        elif self.frequency == Frequency.WEEKLY:
            # Find next occurrence of the same weekday
            days_ahead = (self.start_date.weekday() - today.weekday()) % 7
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            return today + timedelta(days=days_ahead)
        elif self.frequency == Frequency.MONTHLY:
            # Same day next month, handling edge cases
            target_day = self.start_date.day
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1)
            else:
                next_month = today.replace(month=today.month + 1)
            try:
                return next_month.replace(day=target_day)
            except ValueError:
                # Use last day of next month if target day doesn't exist
                if next_month.month == 2:
                    return date(next_month.year, 2, 29) if (next_month.year % 4 == 0 and (next_month.year % 100 != 0 or next_month.year % 400 == 0)) else date(next_month.year, 2, 28)
                else:
                    return next_month.replace(day=1) - timedelta(days=1)
        return today

    def mark_complete_and_reschedule(self):
        """Mark task complete and reschedule for next occurrence if recurring."""
        self.mark_complete()
        if self.frequency in (Frequency.DAILY, Frequency.WEEKLY, Frequency.MONTHLY):
            self.start_date = self.get_next_due_date()
            self.completed = False  # Reset for the new cycle
            self.scheduled_time = None  # Clear old schedule

    def get_description(self) -> str:
        """Return a formatted one-line description of the task including status and schedule."""
        time_str = self.scheduled_time.strftime("%I:%M %p") if self.scheduled_time else "unscheduled"
        status = "done" if self.completed else "pending"
        return (
            f"[{status}] {self.task_type} for {self.pet.name} | "
            f"{self.duration} min | priority {self.priority} | "
            f"{self.frequency.value} | {time_str}"
        )

# Owner holds list of pets and available hours
class Owner:
    def __init__(self, name: str, available_hours: List[int] = None, preferences: Dict[str, Any] = None):
        self.name = name
        self.available_hours = available_hours if available_hours is not None else []
        self.preferences = preferences if preferences is not None else {}
        self.pets: List[Pet] = []

    # --- pet management ---

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str):
        """Remove the pet with the given name from this owner's pet list."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Return the Pet with the given name, or None if not found."""
        for p in self.pets:
            if p.name == pet_name:
                return p
        return None

    # --- task access across all pets ---

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_constraints(self) -> Dict[str, Any]:
        """Return the owner's scheduling constraints (available hours and preferences)."""
        return {
            "available_hours": self.available_hours,
            "preferences": self.preferences,
        }

# This is like a manager that schedules and manages all tasks by priority
class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.daily_plan: List[Dict[str, Any]] = []
        self.conflicts: List[Dict[str, Any]] = []
        self.logger = ConflictLogger()

    # --- task routing (delegates to the correct pet) ---

    def add_task(self, task: Task):
        """Add a task directly to its pet's task list."""
        task.pet.add_task(task)

    def remove_task(self, task_id: int):
        """Remove a task by id from whichever pet owns it."""
        for pet in self.owner.pets:
            pet.remove_task(task_id)

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Find and return a task by its id, or None if not found."""
        for task in self.owner.get_all_tasks():
            if task.id == task_id:
                return task
        return None

    # --- plan generation ---

    def generate_plan(self, for_date: date):
        """
        Build daily_plan for for_date:
        1. Collect all tasks due on that date across every pet.
        2. Sort by priority (1 = highest), then by duration (longest first), then by pet name.
        3. Slot each task into the owner's available times in a contiguous duration-aware way.
        """
        due_tasks = [
            task
            for pet in self.owner.pets
            for task in pet.tasks
            if task.is_due_on(for_date) and not task.completed
        ]
        due_tasks.sort(key=lambda t: (t.priority, -t.duration, t.pet.name))

        constraints = self.owner.get_constraints()
        available_hours = sorted(set(constraints.get("available_hours", [])))

        # Convert hour-based availability into minute-level intervals (no merging for simplicity).
        available_intervals = []  # list of (start_minute, end_minute)
        for hour in available_hours:
            start = hour * 60
            end = start + 60
            available_intervals.append((start, end))

        def find_and_lock_slot(duration_min: int):
            for idx, (start, end) in enumerate(available_intervals):
                if end - start >= duration_min:
                    task_start = start
                    new_start = start + duration_min
                    if new_start == end:
                        available_intervals.pop(idx)
                    else:
                        available_intervals[idx] = (new_start, end)
                    return task_start
            return None

        self.daily_plan = []
        self.conflicts = []

        # ensure recurring tasks not left with old slots
        for task in due_tasks:
            task.scheduled_time = None

        for task in due_tasks:
            start_minute = find_and_lock_slot(task.duration)
            if start_minute is not None:
                task_hour = start_minute // 60
                task_minute = start_minute % 60
                task.scheduled_time = time(task_hour, task_minute)
            else:
                task.scheduled_time = None
                self.conflicts.append({
                    "task_id": task.id,
                    "pet": task.pet.name,
                    "task_type": task.task_type,
                    "reason": "no available slot",
                })

            scheduled_hour = task.scheduled_time.hour if task.scheduled_time else None
            self.daily_plan.append({
                "task_id": task.id,
                "pet": task.pet.name,
                "task_type": task.task_type,
                "priority": task.priority,
                "duration": task.duration,
                "scheduled_hour": scheduled_hour,
                "completed": task.completed,
            })

        # Detect time overlaps after scheduling
        time_conflicts = self.detect_time_conflicts()
        self.conflicts.extend(time_conflicts)

    def mark_task_complete(self, task_id: int):
        """Mark a task complete by id and sync the daily plan entry.

        For recurring tasks, reschedule for next occurrence.
        """
        task = self.get_task_by_id(task_id)
        if task:
            task.mark_complete_and_reschedule()
            for entry in self.daily_plan:
                if entry["task_id"] == task_id:
                    entry["completed"] = True

    def get_plan_summary(self) -> str:
        """Return a single-string summary of the most recent plan and any conflicts."""
        if not self.daily_plan:
            return "No schedule has been generated yet."

        lines = ["Today's schedule:"]
        for entry in sorted(self.daily_plan, key=lambda e: (e["scheduled_hour"] is None, e["scheduled_hour"] if e["scheduled_hour"] is not None else 999)):
            if entry["scheduled_hour"] is None:
                lines.append(f"- {entry['task_type']} for {entry['pet']} (unscheduled, priority {entry['priority']})")
            else:
                hour = entry["scheduled_hour"]
                lines.append(f"- {hour:02d}:00 - {entry['task_type']} for {entry['pet']} (priority {entry['priority']})")

        if self.conflicts:
            lines.append("Conflicts detected:")
            for conflict in self.conflicts:
                if conflict.get("type") == "time_overlap":
                    lines.append(f"- Time overlap: {conflict['task1']} and {conflict['task2']} ({conflict['time']})")
                else:
                    lines.append(f"- {conflict['task_type']} for {conflict['pet']} ({conflict['reason']})")

        return "\n".join(lines) + "\n" + self.logger.get_warning_summary()

    def get_tasks_sorted_by_time(self, date_for: Optional[date] = None, generate=False) -> List[Task]:
        """Return tasks sorted by scheduled time; generate plan for given date if needed."""
        if generate and date_for:
            self.generate_plan(date_for)

        tasks = [t for t in self.owner.get_all_tasks() if t.scheduled_time is not None]
        return sorted(tasks, key=lambda t: (t.scheduled_time.hour, t.scheduled_time.minute))

    def filter_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
        """Return tasks filtered by pet name and/or completion status."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet.name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def detect_time_conflicts(self) -> List[Dict[str, Any]]:
        """Detect overlapping scheduled times between any tasks with logging and error recovery.
        
        Iterates through all scheduled tasks and checks for time overlaps using interval comparison.
        Logs warnings for each detected conflict without raising exceptions.
        
        Returns:
            List[Dict[str, Any]]: List of conflict dictionaries with details.
        """
        conflicts = []
        scheduled_tasks = [t for t in self.owner.get_all_tasks() if t.scheduled_time is not None]
        
        for i, task1 in enumerate(scheduled_tasks):
            try:
                start1 = task1.scheduled_time
                end1 = (datetime.combine(date.today(), start1) + timedelta(minutes=task1.duration)).time()
                
                for task2 in scheduled_tasks[i+1:]:
                    try:
                        start2 = task2.scheduled_time
                        end2 = (datetime.combine(date.today(), start2) + timedelta(minutes=task2.duration)).time()
                        
                        if start1 < end2 and start2 < end1:
                            conflict = {
                                "type": "time_overlap",
                                "task1": f"{task1.task_type} for {task1.pet.name}",
                                "task2": f"{task2.task_type} for {task2.pet.name}",
                                "time":  f"{start1.strftime('%H:%M')}-{end1.strftime('%H:%M')} overlaps {start2.strftime('%H:%M')}-{end2.strftime('%H:%M')}"
                            }
                            conflicts.append(conflict)
                            
                            # Log warning without crashing
                            self.logger.log_warning(
                                f"Time overlap detected: {conflict['task1']} conflicts with {conflict['task2']}",
                                level=WarningLevel.WARNING,
                                metadata=conflict
                            )
                    except Exception as e:
                        # Recover from task2 processing errors
                        self.logger.log_warning(
                            f"Error checking overlap for task {task2.id}: {str(e)}",
                            level=WarningLevel.INFO
                        )
                        continue
                        
            except Exception as e:
                # Recover from task1 processing errors
                self.logger.log_warning(
                    f"Error processing task {task1.id}: {str(e)}",
                    level=WarningLevel.INFO
                )
                continue

        return conflicts
