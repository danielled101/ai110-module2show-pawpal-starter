# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan
Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

#add pet, add/edit tasks, generate a daily plan (schedule) or pet
- Owner: add name, add pet Method: add pet/remove pet, get tasks
- Pet: Add pet name, breed, age, tasks Method: add task, remove task, get task
- Task: description, time, frequency, priority, completed Method: mark completed
- Scheduler: owner Method: sort by time, filter tasks, detect conflicts, recurring tasks


## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

========================================
       Today's Schedule
========================================

Biscuit (Golden Retriever)
------------------------------
  [HIGH] Feeding — 10 min (daily)
  [HIGH] Morning walk — 30 min (daily)
  [MEDIUM] Evening walk — 20 min (daily)

Luna (Tabby Cat)
------------------------------
  [HIGH] Medication — 5 min (daily)
  [HIGH] Feeding — 10 min (daily)
  [LOW] Playtime — 15 min (weekly)

========================================
```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically by their `"HH:MM"` `time` field, tie-broken by priority (HIGH first). |

| Filtering | `Scheduler.filter_tasks()` | Filters by completion status (`completed=True/False`) and/or pet name (`pet_name=...`), searching across all of an owner's pets when no explicit task list is given. Also excludes tasks whose `due_date` is still in the future. |

| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.detect_time_conflicts()` | `detect_conflicts()` flags tasks that would push the day over `max_daily_minutes`. `detect_time_conflicts()` groups today's tasks by exact `time` value (O(n), one dict pass) and returns human-readable warning strings for same-time collisions — same pet or across pets — instead of raising an exception. |

| Recurring tasks | `Task.mark_completed()`, `Scheduler.complete_task()` | `mark_completed()` computes the next occurrence's `due_date` using `timedelta` (+1 day for DAILY, +7 days for WEEKLY); ONCE tasks don't recur. `Scheduler.complete_task()` marks a task done and automatically adds the next occurrence to the pet's task list. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
