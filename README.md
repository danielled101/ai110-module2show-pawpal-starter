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

Today's Schedule
========================================
Biscuit (Golden Retriever)
 - [HIGH] Feeding — 10 min (daily)
 - [HIGH] Morning walk — 30 min (daily)
 - [MEDIUM] Evening walk — 20 min (daily)

Luna (Tabby Cat)
------------------------------
 - [HIGH] Medication — 5 min (daily)
 - [HIGH] Feeding — 10 min (daily)
 - [LOW] Playtime — 15 min (weekly)

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```
The tests confirm task creation, completion, and filtering all work correctly. They verify recurrence — daily/weekly tasks generate a correctly-dated next occurrence, one-time tasks don't recur, and new occurrences stay hidden until actually due, even across multiple cycles. They check sorting puts tasks in time order with priority as a tie-breaker, and handles empty lists safely. They verify conflict detection flags same-time clashes within and across pets while ignoring completed or not-yet-due tasks, and that the daily time-budget logic flags oversized tasks without over-blocking, allows an exact-limit task, and excludes by identity rather than value. Finally, they cover removing tasks/pets and scheduling for a pet with no tasks.

- Confidence level: 4

Sample test output:

========================== test session starts ============================
platform win32 -- Python 3.13.14, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\devos\github\ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 32 items                                                                                                                                          

tests\test_pawpal.py ................................                                      [100%]

============================ 32 passed in 0.09s ============================
```

**## ✨ Features**

- **Sorting by time** — Every schedule is ordered chronologically by each task's `"HH:MM"` time, with same-time ties broken by priority (HIGH → MEDIUM → LOW).
- **Task filtering** — Pull tasks by completion status, by pet name, or both at once, across a single pet or the owner's whole household.
- **Daily & weekly recurrence** — Completing a recurring task automatically generates its next occurrence, due exactly one day (DAILY) or one week (WEEKLY) later; one-time tasks never resurface.
- **Due-date awareness** — A recurring task's next occurrence stays hidden from the schedule until it's actually due, so completing today's walk doesn't clutter today's plan with tomorrow's.
- **Time-conflict warnings** — The scheduler flags any two tasks booked for the same clock time, whether they belong to the same pet or different pets, with a plain-English warning instead of a silent clash.
- **Daily time-budget conflicts** — Tasks that would push a pet's day past a configurable time budget are flagged and excluded from the plan, without wrongly blocking smaller tasks scheduled after them.
- **Multi-pet households** — One owner can track any number of pets, each with its own independent task list.
- **Interactive scheduling UI** — Add tasks with a time picker, mark tasks complete, and generate a live daily plan with conflict warnings, all from the Streamlit app.

**## 📐 Smarter Scheduling**

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically by their `"HH:MM"` `time` field, tie-broken by priority (HIGH first). |

| Filtering | `Scheduler.filter_tasks()` | Filters by completion status (`completed=True/False`) and/or pet name (`pet_name=...`), searching across all of an owner's pets when no explicit task list is given. Also excludes tasks whose `due_date` is still in the future. |

| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.detect_time_conflicts()` | `detect_conflicts()` flags tasks that would push the day over `max_daily_minutes`. `detect_time_conflicts()` groups today's tasks by exact `time` value (O(n), one dict pass) and returns human-readable warning strings for same-time collisions — same pet or across pets — instead of raising an exception. |

| Recurring tasks | `Task.mark_completed()`, `Scheduler.complete_task()` | `mark_completed()` computes the next occurrence's `due_date` using `timedelta` (+1 day for DAILY, +7 days for WEEKLY); ONCE tasks don't recur. `Scheduler.complete_task()` marks a task done and automatically adds the next occurrence to the pet's task list. |

**## 📸 Demo Walkthrough**

**### Main UI features**

The Streamlit app (`app.py`) is organized into three steps:

- **Owner & Pet Info** — Enter an owner name, pet name, and species, then save them to start a session.
- **Tasks** — Add tasks with a title, duration, priority, frequency, and a time picker. Every task you add appears in a live table sorted chronologically by `Scheduler.sort_by_time()`. A dropdown below the table lets you select any pending task and mark it complete.
- **Build Schedule** — Generate today's plan for the saved pet. This checks for same-time conflicts across all pets, then displays the filtered, sorted, budget-checked plan as a table with the total scheduled time.

**### Example workflow**

1. Save an owner ("Jordan") and a pet ("Mochi").
2. Add a task — e.g., "Morning walk," 30 minutes, high priority, daily, at 08:00.
3. Add a second task for the same pet at a different time, e.g., "Feeding" at 07:30.
4. Click **Generate schedule** to view today's plan, sorted chronologically with a total duration.
5. Select "Morning walk" from the dropdown and click **Mark complete** — a new pending "Morning walk" task is automatically scheduled for tomorrow, since it recurs daily.

**### Key Scheduler behaviors shown**

- **Sorting** — Tasks always display in chronological order (`Scheduler.sort_by_time()`), regardless of the order they were added in.
- **Conflict warnings** — If two tasks (same pet or different pets) share a time slot, `Scheduler.detect_time_conflicts()` surfaces a warning banner instead of silently double-booking them.
- **Recurrence** — Marking a daily or weekly task complete (`Scheduler.complete_task()`) automatically creates its next occurrence, which stays hidden from the plan until it's actually due.
- **Budget conflicts** — `Scheduler.detect_conflicts()` excludes tasks that would push the day past the time budget, without wrongly blocking smaller tasks that come after them.

**### Sample CLI output**

Running `python main.py` builds Biscuit and Luna's schedules from hardcoded sample data and prints the full flow — today's schedule, a completed-tasks filter, a per-pet filter, and a conflict check (Biscuit's 08:00 walk deliberately clashes with Luna's 08:00 medication):

```
========================================
       Today's Schedule
========================================

Biscuit (Golden Retriever)
------------------------------
 - 08:00 [HIGH] Morning walk — 30 min (daily)
 - 18:00 [MEDIUM] Evening walk — 20 min (daily)

Luna (Tabby Cat)
------------------------------
 - 07:45 [HIGH] Feeding — 10 min (daily)
 - 08:00 [HIGH] Medication — 5 min (daily)
 - 17:00 [LOW] Playtime — 15 min (weekly)

Already completed today:
  - Feeding

Luna's tasks only (filter by pet name):
  - 07:45 Feeding
  - 08:00 Medication
  - 17:00 Playtime

Schedule conflict check:
  WARNING: Time conflict at 08:00: Morning walk (Biscuit), Medication (Luna)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
