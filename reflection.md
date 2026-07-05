# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

My initial UML design modeled a pet care scheduling system with four classes connected by ownership relationships: an owner manages pets, each pet holds its own tasks, and a scheduler reads from the owner to build a daily plan.

- What classes did you include, and what responsibilities did you assign to each?

Owner — stores the owner's name and their list of pets; responsible for adding and removing pets.
Pet — stores the pet's name, breed, and age; responsible for managing its own task list via add_task, remove_task, and get_tasks.
Task — stores a care item's description, duration in minutes, frequency, priority, and completion status; responsible for marking itself completed.
Scheduler — takes an Owner as input; responsible for sorting tasks by time, filtering tasks that fit the day's constraints, and detecting scheduling conflicts.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The main issues were that the Scheduler had no clear path to actually reach tasks, its methods took no inputs so they had nothing to work with, and frequency and priority were open text fields that could silently break from a typo. To fix this, Frequency and Priority enums were added so those fields only accept a set list of valid values. A generate_plan(pet) method was added to the Scheduler as a clear entry point — you pass in a specific pet and it handles the rest. The helper methods sort_by_time and filter_tasks were updated to take a task list as input, and detect_conflicts was updated to take the already-scheduled tasks so it actually has something to compare. The UML diagram was also updated to reflect all of these changes.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

`detect_time_conflicts` only checks whether two tasks share the exact same `time` value (e.g., both at "08:00"), rather than checking whether their full duration ranges actually overlap. A 30-minute walk starting at 08:00 and a 5-minute medication task starting at 08:20 would genuinely overlap in real life, but since their `time` strings don't match exactly, my scheduler won't flag them as a conflict.

- Why is that tradeoff reasonable for this scenario?

Exact-match detection can be done with a single dict grouped by time string in one pass over the day's tasks (group by time, then flag any group with more than one task). Real overlap detection would instead require sorting tasks by start time and comparing each task's [start, start + duration] window against its neighbors — more moving parts for a hobby app with only a handful of tasks per pet per day. I picked the simpler version because it still catches the mistake I actually cared about (accidentally scheduling two things at the same moment), it was easier to reason about and test, and a full interval-overlap engine felt like more complexity than this scenario needed.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
