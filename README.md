# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

# AI - Content
## Smarter Scheduling

This version includes advanced scheduling features for better pet care management:

- **Time-based sorting**: Tasks can be sorted by scheduled time using `sort_by_time()` for chronological ordering.
- **Flexible filtering**: Filter tasks by pet name or completion status with `filter_tasks(pet_name, completed)`.
- **Recurring task support**: Daily, weekly, and monthly tasks automatically reschedule after completion using `mark_complete_and_reschedule()`.
- **Conflict detection**: Detects time overlaps between tasks and logs warnings without crashing the program, ensuring robust scheduling.

These features make PawPal+ more intelligent and user-friendly for managing complex pet care routines.

=================================
## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
