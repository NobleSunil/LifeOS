# LifeOS — Complete Project Documentation

**Version:** 1.0  
**Framework:** Django 6.0.3  
**Database:** SQLite  
**Date:** March 2026

---

# SECTION 1 — PROJECT OVERVIEW

## What is LifeOS?

LifeOS is a personal productivity web application built with Django. It helps individuals manage their goals, track daily tasks, build consistent habits, reflect on their progress, and generate productivity reports — all in one place.

## What Problem Does It Solve?

Most people struggle with three core productivity problems:

1. **They set goals but forget them** — No system connects big goals to daily tasks.
2. **They start habits but lose consistency** — No tracking means no accountability.
3. **They work hard but can't measure progress** — No data means no insight.

LifeOS solves all three by tying Goals → Tasks → Habits → Reflections into a single connected system.

## Who Is It For?

LifeOS is designed for students, professionals, and anyone who wants to become more intentional about how they spend their time. It is especially useful for people who:

- Have multiple goals they are working towards simultaneously
- Want to build daily habits and track streaks
- Like data and want to see their productivity over time
- Want a private daily journal for reflection

## What Makes It Different From a Simple To-Do App?

A regular to-do app just lets you write tasks and check them off. LifeOS adds:

- **Goal linking** — Every task can be tied to a big goal, so every checkbox moves you closer to something meaningful
- **Three types of habit tracking** — Slider (how much?), Checkbox (did I or didn't I?), and Task-Driven (automatic from task progress)
- **Productivity scoring** — A daily score calculated from both tasks completed and habits logged
- **Reflective journaling** — A structured daily journal with Wins, Challenges, and Tomorrow's Plan
- **Admin analytics** — Platform-level insights for an administrator to see how users are engaging

## Core Concept

```
Goals  ──────────────────────────────────────────────────
  │                                                      │
  ├── Tasks (Simple or Trackable) ──► Completion ──► Goal Progress %
  │
  └── Habits ──► Daily Logs ──► Streaks ──► Habit Progress
                                               │
                                               ▼
                                     Dashboard Score &
                                     Productivity Graph

Reflections ──► Daily Journal ──► Streak
Reports     ──► CSV Export    ──► Self Review
```

---

# SECTION 2 — TECH STACK

## Backend — Django (Python) 6.0.3

**What it is:** Django is a high-level Python web framework.

**Why chosen:** Django provides built-in authentication, admin tools, ORM (database queries written in Python), form validation, CSRF protection, and session management — all out of the box. This reduced development time significantly.

**How used in this project:**
- Handles all URL routing, request/response processing
- Manages user authentication (login, logout, register, session)
- ORM is used for all database operations (no raw SQL)
- Template engine renders HTML pages with dynamic data
- Built-in CSRF middleware protects all forms

## Database — SQLite

**What it is:** A lightweight, file-based SQL database. The database is stored as a single file: `db.sqlite3` in the project root.

**Why chosen:** SQLite requires no separate server installation, making it ideal for development and small-scale deployment.

**How used:** Stores all data — users, goals, tasks, habits, completions, reflections.

**Limitation:** Not suitable for production deployments with many concurrent users. Should be replaced with PostgreSQL for production.

## Frontend — HTML + Vanilla CSS + Bootstrap (partial)

**What it is:** Standard web technologies for structuring and styling pages.

**Why chosen:** Bootstrap utility classes provide quick responsive layout. Custom CSS in `static/css/style.css` handles the full design system including CSS variables, dark-mode-ready colors, and component-level styles.

**How used:**
- `base.html` is the master template all pages extend
- Custom CSS variables (`--primary-color`, `--border-color`, etc.) used throughout for consistent theming
- `Outfit` and `Playfair Display` fonts loaded from Google Fonts
- All modals are custom-built without Bootstrap JS (pure CSS/JS)

## Charts — Chart.js (CDN)

**What it is:** A JavaScript library for rendering canvas-based charts.

**Why chosen:** Simple API, no installation required, works well with Django template-injected JSON data.

**How used:**
- Dashboard: 7-day productivity line chart
- Admin: 30-day platform activity bar chart, user count pie chart, habits analytics bar chart, age group donut chart

## Authentication — Django Built-in Auth

**What it is:** Django's `django.contrib.auth` module provides a complete authentication system.

**How used:**
- `User` model is the core user object
- `@login_required` decorator protects all private views
- `CustomLoginView` extends `LoginView` to redirect admins to the admin panel
- Password hashing handled automatically by Django
- Sessions used to keep users logged in
- `UserProfile` extends the built-in User with additional fields (full name, bio, age)

## Other Dependencies

| Dependency | Purpose |
|---|---|
| `csv` (Python stdlib) | Report CSV generation |
| `json` (Python stdlib) | Passing data from Django to JavaScript |
| `datetime` (Python stdlib) | Date calculations, streaks, chart labels |
| `calendar` (Python stdlib) | Building the reflection calendar grid |
| Google Fonts API | Loading Outfit and Playfair Display fonts |
| Chart.js (CDN) | All charts and data visualizations |

---

# SECTION 3 — DATA MODELS & RELATIONSHIPS

## Relationship Overview

```
User (Django built-in)
 ├── UserProfile (OneToOne) — extends User with name, bio, age
 │
 ├── Goal (ForeignKey on user)
 │    ├── Task (ForeignKey on goal — optional link)
 │    └── Habit (ForeignKey on goal — optional link)
 │
 ├── Task (ForeignKey on user)
 │    ├── goal → Goal (SET_NULL on delete)
 │    └── habit → Habit (SET_NULL on delete)
 │
 ├── Habit (ForeignKey on user)
 │    ├── goal → Goal (SET_NULL on delete)
 │    └── HabitCompletion (ForeignKey on habit — CASCADE)
 │
 └── Reflection (ForeignKey on user)
```

---

## Model 1 — UserProfile

**Purpose:** Stores extra profile information about a user beyond what Django's built-in User model provides.

| Field | Type | Purpose |
|---|---|---|
| `user` | OneToOneField → User | Links to the Django User. Deleted if user is deleted (CASCADE). |
| `full_name` | CharField (200) | User's display name shown on dashboard |
| `bio` | TextField | Optional personal description |
| `age` | IntegerField | Optional, used in admin age analytics |

**Relationship:** One-to-one with `User`. Every user has at most one profile.

---

## Model 2 — Goal

**Purpose:** Represents a long-term objective a user is working towards.

| Field | Type | Purpose |
|---|---|---|
| `user` | ForeignKey → User | Owner of the goal (deleted with user) |
| `title` | CharField (200) | Name of the goal |
| `description` | TextField | Optional longer description |
| `status` | CharField | 'Active' or 'Completed' |
| `created_at` | DateTimeField | Auto-set on creation |
| `completed_at` | DateTimeField | Set when goal is marked complete |

**Computed Properties (on the model):**
- `total_tasks` — count of all linked tasks
- `completed_tasks` — count of completed linked tasks
- `progress_percentage` — `(completed / total) * 100`, returns 0 if no tasks

**Relationships:**
- Belongs to one `User`
- Can have many `Task`s linked (via `tasks` related name)
- Can have many `Habit`s linked (via `habits` related name)

---

## Model 3 — Habit

**Purpose:** Represents a recurring activity a user wants to log every day.

| Field | Type | Purpose |
|---|---|---|
| `user` | ForeignKey → User | Owner of the habit |
| `habit_name` | CharField (200) | Name of the habit |
| `goal` | ForeignKey → Goal | Optional, links habit to a goal. SET_NULL if goal deleted. |
| `tracking_mode` | CharField | How the habit is logged (see choices below) |
| `created_at` | DateTimeField | Auto-set on creation |

**Tracking Mode Choices:**

| Value | Label | Meaning |
|---|---|---|
| `manual_slider` | Manual with Slider | User drags a 0–100% slider each day |
| `manual_checkbox` | Manual with Checkbox | User clicks "Mark Done" (100%) or "Not Done" (0%) |
| `task_driven` | Task Driven | Auto-calculated from linked trackable tasks' average progress |

**Important:** `tracking_mode` cannot be changed after creation. It is locked in the form.

**Relationships:**
- Belongs to one `User`
- Optionally belongs to one `Goal`
- Has many `HabitCompletion` records (one per day logged)
- Can have many `Task`s linked to it for task-driven mode

---

## Model 4 — HabitCompletion

**Purpose:** Records how much of a habit was completed on a specific date.

| Field | Type | Purpose |
|---|---|---|
| `habit` | ForeignKey → Habit | Which habit was logged (deleted with habit, CASCADE) |
| `date` | DateField | The date of this log entry |
| `completion_percentage` | IntegerField | 0 to 100, how much was done |

**Constraint:** `unique_together = ('habit', 'date')` — only one log entry per habit per day.

**Relationships:** Belongs to one `Habit`. Many completions exist per habit (one per day logged).

---

## Model 5 — Task

**Purpose:** Represents a single action item a user needs to complete.

| Field | Type | Purpose |
|---|---|---|
| `user` | ForeignKey → User | Owner of the task |
| `title` | CharField (200) | Name of the task |
| `description` | TextField | Optional longer explanation |
| `status` | CharField | 'Pending' or 'Completed' |
| `task_type` | CharField | 'simple' or 'trackable' (locked after creation) |
| `progress` | IntegerField (0–100) | Current progress % (trackable tasks only) |
| `goal` | ForeignKey → Goal | Optional link to a goal. SET_NULL if goal deleted. |
| `habit` | ForeignKey → Habit | Optional link to a habit. SET_NULL if habit deleted. |
| `start_date` | DateField | Optional start date |
| `due_date` | DateField | Optional due date |
| `created_at` | DateTimeField | Auto-set on creation |

**Task Types:**
- **Simple** — Binary. Either Pending or Completed.
- **Trackable** — Has a 0-100% progress slider. Can be gradually updated. Also has Complete button.

**Relationships:**
- Belongs to one `User`
- Optionally belongs to one `Goal`
- Optionally belongs to one `Habit` (used for task-driven habit calculation)

---

## Model 6 — Reflection

**Purpose:** Stores a user's daily journal entry.

| Field | Type | Purpose |
|---|---|---|
| `user` | ForeignKey → User | Owner of the reflection |
| `date` | DateField | The date this reflection is for |
| `content` | JSONField | `{"wins": "...", "challenges": "...", "tomorrow": "..."}` |
| `created_at` | DateTimeField | Auto-set on creation |

**Constraint:** `unique_together = ('user', 'date')` — only one reflection per user per day.

**JSON Content Structure:**

```json
{
  "wins": "What I accomplished today",
  "challenges": "What was difficult",
  "tomorrow": "What I will focus on tomorrow"
}
```

---

# SECTION 4 — FEATURES & FUNCTIONALITY

## 1. User Registration & Login

**What it does:** Allows new users to create an account and existing users to sign in.

**Registration fields:** Username, Email, Password, Confirm Password, Age (optional)

**Backend process:**
1. Form validates that passwords match
2. Django creates a `User` object with hashed password
3. A `UserProfile` is created automatically with the age provided
4. User is logged in immediately and redirected to Dashboard

**Login process:**
- Django's built-in `LoginView` handles authentication
- Admin users (superusers) are redirected to `/admin-panel/overview/`
- Regular users are redirected to `/` (Dashboard)

**Edge cases:** Already-logged-in users visiting `/register/` or `/login/` are immediately redirected to the dashboard.

---

## 2. Dashboard

**What it does:** The home page showing a summary of the user's entire life at a glance.

### Greeting
- Shows "Good Morning", "Good Afternoon", or "Good Evening" based on current hour
- Uses the user's first name from their profile (falls back to username if no profile)

### Motivational Quote
- Rotates daily from a hardcoded list of 7 quotes
- Quote is chosen using `today.toordinal() % 7` — same quote all day, changes at midnight

### Quick Stats (3 cards)
| Stat | What it shows |
|---|---|
| Tasks Due Today | Count of Pending tasks with `start_date <= today` |
| Active Goals | Count of Goals with `status = 'Active'` |
| Habits Logged | Count of distinct habits logged today |

### Today's Tasks
- Shows all Pending tasks where `start_date <= today`
- Sorted: Overdue first → Due today → Future
- Each task shows a colored label: red (overdue), orange (due today), blue (future)

### Goal Progress
- Lists all Active goals with a progress bar
- Bar color: Red (0-30%), Yellow (31-70%), Green (71-100%)

### Today's Habits
- Lists all habits with their today's completion percentage
- Shows streak (consecutive days logged)
- Color coded: Grey (0%), Red (1-29%), Yellow (30-69%), Green (70-100%)

### Productivity Graph
- Line chart showing the last 7 days' productivity scores
- Score = average of (Task Score + Habit Score) / 2 per day
- Built with Chart.js, data passed as JSON from Django view

### Floating Action Button (FAB)
- Plus button fixed to bottom-right corner
- Opens a modal with quick links to Add Task and Log Habit

---

## 3. Goals Module

### Create Goal
- Click "+ New Goal" → modal form appears
- Fields: Title (required), Description (optional), Status (Active/Completed)
- Saved with the current user automatically assigned

### Edit Goal
- Click "Edit" on any goal → same modal pre-filled with existing data
- All fields can be edited

### Delete Goal
- Click "Delete" → confirmation dialog → goal deleted
- When a goal is deleted: linked Tasks and Habits are NOT deleted, their `goal` field is set to NULL (`SET_NULL`)

### Goal Progress Tracking
- Calculated as: `(completed tasks / total tasks) * 100`
- Displayed as a colored progress bar on both Goals page and Dashboard
- Progress bar colors: Red → Yellow → Blue → Green as progress increases

### Mark Goal Complete
- "Mark Complete" button sets `status = 'Completed'` and records `completed_at` timestamp
- Completed goals are shown in a separate section below Active goals

### Inline Expand View
- Each goal card is collapsible — click to expand/collapse details
- Expanded view shows task count, habit count, progress bar, and action buttons

---

## 4. Tasks Module

### Create Task
- Click "+ New Task" → modal form
- Fields: Title, Description, Start Date, Due Date, Status, Task Type, Link to Goal, Link to Habit
- Task Type (Simple/Trackable) is selected at creation and **cannot be changed later**

### Task Types

**Simple Task:**
- Works like a classic to-do item
- Has only a "✓ Complete" button and Edit/Delete
- Completing sets `status = 'Completed'`

**Trackable Task:**
- Shows a 📊 badge with current progress percentage
- Has a 0–100% progress slider below the card
- "Save Progress" button saves the value
- At 100%, a "💡 Mark as Complete" prompt appears
- Clicking "✓ Complete" sets `status = 'Completed'` AND `progress = 100`

### Task Progress Slider (Trackable)
- Live value display updates as slider is dragged (via `updateSliderValue()` JS function)
- Submit sends a POST to `/tasks/<id>/progress/`
- Backend saves the progress value and recalculates any linked task-driven habit

### Grouped Sections
Tasks page organises tasks into four sections:
1. ⚠️ **Overdue** — tasks with `due_date < today`
2. 📌 **Today** — tasks with `due_date == today`
3. 📋 **Pending** — all other pending tasks
4. ✅ **Completed** — all completed tasks (collapsible)

### Filter System
Three tab filters: **All**, **Today**, **Overdue**
Two dropdown filters: **By Goal**, **By Habit**

All filtering is done client-side in JavaScript using `data-*` attributes on each task card.

### Goal & Habit Linking
- A task can be linked to one Goal (optional)
- A task can be linked to one Habit (optional)
- Linking to a habit enables the Task Driven habit mode
- When deleting a goal or habit, linked tasks are NOT deleted — their foreign key is set to NULL

---

## 5. Habits Module

### Create Habit
- Click "+ New Habit" → modal form
- Fields: Habit Name, Link to Goal, Tracking Mode
- Tracking Mode is chosen at creation and **cannot be changed later**

### Edit Habit
- Opens same modal pre-filled
- Tracking mode is disabled (locked) and shown as read-only
- Name and Goal link can be changed

### Delete Habit
- Confirmation → deletes the habit and ALL its HabitCompletion records (CASCADE)

### Manual Slider Mode
- Habit card shows a 0–100% slider when expanded
- User drags to set today's completion and clicks "Save Log"
- Saves a HabitCompletion record for today

### Manual Checkbox Mode
- Habit card shows "✅ Mark Done" and "❌ Not Done" buttons
- "Mark Done" saves 100%, "Not Done" saves 0%
- Weekly view shows ✅ / ❌ / ⬜ for each day

### Task Driven Mode
- No manual logging — habit progress is calculated automatically
- When a linked trackable task's progress is saved, the habit's log for today is recalculated
- Calculation: Average progress of all trackable tasks linked to this habit
- If no trackable tasks are linked, a ⚠️ warning is shown
- Weekly view shows colour-coded percentage bars

### Streak Tracking
- Displayed on each habit card as "🔥 X days"
- Streak counts consecutive days where `completion_percentage > 0`
- For checkbox mode: streak counts days where `completion_percentage == 100`
- If today isn't logged yet, streak looks back from yesterday

### Weekly View
- Shows the last 7 days for each habit
- Slider/Task-Driven: colour-coded dots (🔴 < 30, 🟡 30–69, 🟢 ≥ 70)
- Checkbox: ✅ (100%) / ❌ (0%) / ⬜ (no log)

### Goal Linking
- A habit can be linked to one goal
- Linking shows in both the Goals page count and the Habit card

---

## 6. Reflection Module

### Daily Journal
- One reflection per user per day (enforced by `unique_together` constraint)
- Three structured sections: Wins 🏆, Challenges ⚡, Tomorrow's Plan 🎯
- Today's form auto-loads existing content if already written

### Calendar View
- Shows the current month as a grid
- Days with reflections show ✅, today shows 📝, empty days show ——
- Clicking any day with a reflection loads it in read-only view below the calendar
- Navigation arrows to browse past months (cannot go to future months)

### Edit Past Reflection
- In the read-only view, click "✏️ Edit" to load the content into the editable form
- The form action changes to `/reflections/edit/<id>/` via JavaScript
- After saving, shows updated content

### Cancel Today's Reflection
- A "🗑️ Cancel Today" button appears next to "Save Reflection" **only if** today's reflection already exists
- Confirmation dialog → deletes today's reflection → today's form resets to blank

### Structured Sections
All three sections (Wins, Challenges, Tomorrow) are stored in a single JSON field in the database. Each section is displayed in its own labelled card.

### Reflection Streak
- Shown on the Reflections page header as "🔥 X days"
- Counts consecutive days with a reflection up to and including today
- If today has no reflection, streak is from yesterday backwards

---

## 7. Reports Module

### Date Range Selection
- User picks a start date and end date from date pickers
- Minimum date is the user's registration date (cannot request data before account existed)
- An AJAX call to `/reports/summary/` returns live counts for the selected range

### Summary Preview
Before downloading, the user sees counts of:
- Tasks created in range
- Habit logs in range
- Goals created in range
- Reflections in range

### CSV Export
- User selects which sections to include (Tasks, Habits, Goals, Reflections)
- Clicking "Generate Report" downloads a `.csv` file named `LifeOS_Report_<from>_to_<to>.csv`
- Each section is separated by headers in the CSV

**CSV Columns:**

| Section | Columns |
|---|---|
| Tasks | Title, Description, Status, Start Date, Due Date, Linked Goal, Linked Habit, Created At |
| Habits | Habit Name, Linked Goal, Date, Completion % |
| Goals | Title, Description, Status, Progress %, Tasks Linked, Habits Linked, Created At |
| Reflections | Date, Wins, Challenges, Tomorrow's Plan |

---

## 8. Admin Panel

### Overview
- Shows platform-wide statistics: total users, active users, total goals, tasks, habits, average habit completion rate
- Active users = users who have done ANY activity (task, habit log, or reflection) in the last 7 days

### User Management
- List of all regular users (superusers excluded)
- Search by username or email
- Filter by active/inactive status
- Toggle a user's active/inactive status (enable/disable their login)

### Activity Chart
- 30-day bar chart showing daily platform activity
- Activity score per day = tasks completed + habits logged that day across all users

### Habits Analytics
- Top 5 most popular habits (by name, across all users)
- Top 5 most active users (by number of habit logs)

### Consistency Leaderboard
- Ranks users by their average productivity score across all their active days
- Only users with 5+ active days appear
- Score = average of (habit score + task score) / 2 per active day

### Age Analytics
- Users grouped by age: 15-20, 21-25, 26-30, 30+
- Top 5 habits in each age group
- Displayed with a donut chart and breakdown cards

---

# SECTION 5 — LOGIC & CALCULATIONS

## 1. Goal Progress %

**Formula:** `(Number of Completed Tasks linked to Goal / Total Tasks linked to Goal) * 100`

**Example:**
- Goal: "Get fit"
- Total linked tasks: 5
- Completed tasks: 2
- Progress = (2 / 5) * 100 = **40%**

**Edge case:** If a goal has 0 tasks, progress = 0%. The check `if total > 0` prevents division by zero.

**Color coding:**
- 0–30% → Red (danger)
- 31–70% → Yellow/Orange (warning)
- 71–99% → Blue (primary)
- 100% → Green (success)

---

## 2. Task Score (for Dashboard Productivity)

Used in the daily productivity graph for each day in the last 7 days.

**Formula:** `(Tasks Completed on that day / Total Tasks with due_date on that day) * 100`

**Example:**
- 3 tasks were due on Monday
- 2 were completed
- Task Score = (2/3) * 100 = **66.7%**

**Edge case:** If no tasks were due that day, Task Score = 0%.

**Note for Trackable tasks:** The productivity graph uses completion status only (not progress %). A trackable task counts as "complete" only when fully marked Completed.

---

## 3. Habit Score (for Dashboard Productivity)

Used in the daily productivity graph.

**Formula:** Average of all `completion_percentage` values from HabitCompletion records for that day.

**Example:**
- Monday habit logs: Meditation=80%, Exercise=60%, Reading=100%
- Habit Score = (80 + 60 + 100) / 3 = **80%**

**Edge case:** If no habits were logged that day, Habit Score = 0%.

---

## 4. Daily Productivity Score

Shown on the dashboard productivity graph as a single value per day.

**Formula:** `round((Habit Score + Task Score) / 2)`

**Example:**
- Habit Score = 80%, Task Score = 66.7%
- Productivity Score = round((80 + 66.7) / 2) = round(73.35) = **73**

**Average score** shown on dashboard = sum of all 7 daily scores / 7

---

## 5. Habit Streak

Shows how many consecutive days a habit has been logged.

**Formula:**
1. Start from today (or yesterday if today has no log)
2. Walk backwards in time
3. Count days where `completion_percentage > 0`
4. Stop counting when a day with `completion_percentage == 0` or no log is found

**For Manual Checkbox habits:**
- Streak counts only days where `completion_percentage == 100`
- A "Not Done" day (0%) breaks the streak

**Example:**
- Wed: 80%, Tue: 60%, Mon: 100%, Sun: 0% → Streak = **3** (stops at Sun)

**Edge case:** If today has no log, streak looks back from yesterday — so a streak can still be active even if today hasn't been logged yet.

---

## 6. Task Driven Habit % Calculation

When a trackable task linked to a task-driven habit has its progress updated, the habit's log for today is recalculated.

**Formula:** `Average progress % of all trackable tasks linked to this habit`

**Example:**
- Habit: "Build App"
- Linked trackable tasks: Task A = 80%, Task B = 40%, Task C = 100%
- Habit today's completion = (80 + 40 + 100) / 3 = **73.3% → saved as 73%**

**Edge case:**
- If no trackable tasks are linked, the habit shows a ⚠️ warning and progress stays 0%
- If a linked task is deleted, it's unlinked (`SET_NULL`), so the average is recalculated from remaining tasks
- If all tasks are deleted, the habit shows 0% and the ⚠️ warning reappears

---

## 7. Reflection Streak

**Formula:**
1. Start from today
2. Walk backwards day by day
3. Count days where a Reflection exists
4. Stop when a day with no reflection is found

**Example:**
- Today, Yesterday, Day before: all have reflections. 3 days ago: no reflection
- Streak = **3**

**Edge case:** If today has no reflection entry yet, it's not counted — but the streak from previous days still shows.

---

## 8. Admin Active Users Count

**Formula:** Count users who've done ANY of the following in the last 7 days:
- Created a task
- Logged a habit completion
- Written a reflection

**Implementation:** Uses Django's `Q` objects to OR these conditions and `.distinct()` to avoid counting the same user multiple times.

**Edge case:** Superusers are excluded from all admin counts.

---

## 9. Admin Habit Completion Rate

**Formula:** Average `completion_percentage` across all HabitCompletion records from all non-admin users.

**Example:**
- All-time logs: 100%, 80%, 60%, 40%, 0%
- Completion rate = (100+80+60+40+0) / 5 = **56%**

**Edge case:** If no completion records exist, returns 0%.

---

## 10. Admin Consistency Leaderboard Score

This is the most complex calculation in the project.

**Formula per user:**
1. Find all days the user was active (completed a task OR logged a habit)
2. For each active day, calculate a day score:
   - **Habit Score for that day** = average completion % of all habit logs that day
   - **Task Score for that day** = (tasks completed that day / total tasks created up to that day) * 100
   - **Day Score** = (Habit Score + Task Score) / 2
3. User's leaderboard score = average of all day scores

**Users with < 5 active days are excluded** from the leaderboard.

**Example:**
- User has 10 active days
- Day 1: Habit=80, Task=60 → Day Score=70
- Day 2: Habit=100, Task=80 → Day Score=90
- ... (10 days total)
- Average = 78.5 → displayed as **78.5**

---

# SECTION 6 — USER FLOW

## Step 1: Registration

1. Visit the app → redirected to `/login/`
2. Click "Register" link → go to `/register/`
3. Fill in: Username, Email, Password, Confirm Password, Age (optional)
4. Submit → account created, profile created, auto-logged in
5. **Redirected to Dashboard** (`/`)

---

## Step 2: First Login

The dashboard shows empty state messages for each section:
- "No tasks" placeholder
- "No goals" placeholder with motivational text
- "No habits" placeholder
- Productivity graph shows flat line (all zeros)
- A rotating daily quote provides motivation

**Recommended first action:** Create at least one Goal to get started.

---

## Step 3: Setting Up Goals

1. Click "🎯 Goals" in the sidebar
2. Click "+ New Goal"
3. Enter title (e.g., "Learn Django"), optional description, status = Active
4. Click Save → goal appears in the list
5. Goal shows 0% progress and 0 tasks initially
6. Create tasks and link them to this goal to start tracking progress

---

## Step 4: Creating Tasks

**Simple task:**
1. Go to Tasks page (✅ Tasks in sidebar)
2. Click "+ New Task"
3. Fill: Title, optional Description, Dates, select "Simple" (default)
4. Optionally link to a Goal and/or Habit
5. Save → task appears in Pending section

**Trackable task:**
1. Same as above, but select "Trackable" radio button
2. After save → task card shows a 📊 0% badge and progress slider
3. Drag slider to update progress → click "Save Progress"
4. At 100%, a "Mark as Complete" prompt appears

---

## Step 5: Setting Up Habits

**Manual Slider habit:**
1. Go to Habits (💪 Habits in sidebar)
2. Click "+ New Habit"
3. Enter name, optionally link to goal, leave "Manual with Slider" selected
4. Save → habit card appears with 📊 Slider badge
5. Click the card to expand → drag slider → Save Log

**Manual Checkbox habit:**
1. Same as slider, but select "Manual with Checkbox"
2. Expanded card shows ✅ Mark Done / ❌ Not Done buttons

**Task Driven habit:**
1. Same setup, select "Task Driven"
2. Go to Tasks → Edit a trackable task → link it to this habit
3. Now whenever the task's progress is saved, the habit auto-updates
4. No manual logging needed

---

## Step 6: Daily Usage

**Morning:**
- Open Dashboard → review today's tasks and habit status
- Read the day's motivational quote
- Check which tasks are overdue

**During the day:**
- Update trackable task progress via sliders
- Mark simple tasks as complete
- Log habits (slider / checkbox)

**Evening:**
- Write daily reflection at `/reflections/`
- Wins: What did I accomplish?
- Challenges: What was hard?
- Tomorrow: What will I focus on?

---

## Step 7: Tracking Progress

**Goal progress:** Check the Goals page — progress bar shows % complete based on tasks done.

**Productivity graph:** Dashboard shows a 7-day line chart. Aim for consistently high bars.

**Habit streaks:** Each habit card shows current streak. The higher the streak, the stronger the habit.

---

## Step 8: Generating Reports

1. Click "📊 Reports" in sidebar (visible to regular users)
2. Pick a date range using the date pickers
3. Summary counts appear instantly via AJAX
4. Select which sections to include: Tasks, Habits, Goals, Reflections
5. Click "Generate Report" → CSV downloads automatically

---

## Navigation

**Sidebar:**
| Item | Page |
|---|---|
| 🏠 Dashboard | `/` |
| 🎯 Goals | `/goals/` |
| ✅ Tasks | `/tasks/` (shows overdue badge count) |
| 💪 Habits | `/habits/` |
| 📓 Reflection | `/reflections/` |
| 📊 Reports | `/reports/` |

**Profile dropdown (top right):**
- `Q` avatar button → links to `/profile/`
- Profile page allows editing: Full Name, Email, Bio, Age
- Sidebar has Logout link

---

# SECTION 7 — ADMIN FLOW

## How Admin Logs In

The admin (superuser) logs in on the same login page as regular users (`/login/`). After login, the `CustomLoginView` detects `user.is_superuser == True` and redirects to `/admin-panel/overview/` instead of the dashboard.

Regular users who try to visit admin URLs are redirected to the regular dashboard by the `@admin_required` decorator.

---

## Admin Dashboard Overview (`/admin-panel/overview/`)

Shows six key platform metrics:
- Total users on the platform
- Active users (active in last 7 days)
- Total goals ever created
- Total tasks ever created
- Total habits ever created
- Average habit completion rate across all users

---

## Admin User Management (`/admin-panel/users/`)

- Table showing all regular users with their username, email, join date, and status
- Search bar filters by username or email in real time
- Status filter: All / Active / Inactive
- Each user row has a "Disable" or "Enable" toggle button
- Clicking toggle calls `/admin-panel/users/toggle/<user_id>/` which flips `user.is_active`
- A disabled user cannot log in — Django's auth system checks `is_active` automatically

---

## Admin Activity Chart (`/admin-panel/activity/`)

- Shows a 30-day bar chart of total platform activity per day
- Activity = tasks completed + habit completions with > 0% on that day
- Useful for identifying when users are most productive

---

## Admin Habits Analytics (`/admin-panel/habits/`)

- **Top 5 Most Popular Habits** — ranked by how many users created a habit with that name
- **Top 5 Most Active Users** — ranked by total habit log count

---

## Admin Consistency Leaderboard (`/admin-panel/leaderboard/`)

- Shows users ranked by their average daily productivity score
- Only users with 5+ active days are shown (casual users are filtered out)
- Score combines habit completion average + task completion rate
- A higher score means the user is consistently completing both tasks and habits

---

## Admin Age Analytics (`/admin-panel/age/`)

- Shows user count broken into four age groups: 15-20, 21-25, 26-30, 30+
- For each age group, shows the Top 5 habits those users track
- Uses a donut chart for the age distribution
- Users who didn't provide age are not counted in any group

---

## What Admin CANNOT Do

| Limitation | Reason |
|---|---|
| Cannot see individual user data (tasks, reflections) | Privacy — only aggregate data is shown |
| Cannot create tasks/habits/goals for users | Admin role is analytics-only |
| Cannot reset a user's password from this panel | No password management UI built |
| Cannot delete users | No delete functionality in the admin panel |
| Cannot access Django's built-in `/admin/` to modify records | Only the custom admin panel is used in normal flow |

---

## Admin Data Isolation

All admin views filter out superusers using `is_superuser=False`. This means the admin's own test data (if any) never appears in the analytics.

Regular user data is never directly shown to the admin — only counts, averages, and aggregates. Individual reflections, task titles, and personal notes are never exposed.

---

# SECTION 8 — KNOWN LIMITATIONS

## Technical Limitations

| Limitation | Impact | Future Fix |
|---|---|---|
| SQLite database | Cannot handle many concurrent write operations. Not suitable for production. | Migrate to PostgreSQL |
| `DEBUG = True` in settings | Exposes detailed error pages. Secret key is visible in source. | Use environment variables, set DEBUG=False for production |
| No caching layer | Every dashboard load queries the database multiple times | Add Redis/Memcached caching for expensive queries |
| No background tasks | Task-driven habit recalculation runs synchronously on every progress save | Add Celery for async processing |

## Feature Limitations

| Limitation | Impact | Future Fix |
|---|---|---|
| No email notifications | Users can't receive reminders to log habits or write reflections | Add email/push notifications |
| No mobile app | Web-only, no native mobile experience | Build React Native or Flutter app |
| No social/sharing features | Progress is entirely private | Add optional public profiles |
| No sub-tasks | Tasks can't be broken into smaller steps | Add subtask support |
| No recurring tasks | Tasks must be manually re-created | Add recurring task templates |
| No habit templates | Each habit is created from scratch | Add a library of popular habits to choose from |
| Reports only go back to registration | Can't import historical data | Add CSV import feature |

## Logic Limitations

| Limitation | Impact |
|---|---|
| Daily productivity score averages habits and tasks equally (50/50) | A user with many habits but no tasks will score differently than intended |
| Task-driven habit uses ALL linked trackable tasks | If a user links many unrelated tasks, the habit average may be misleading |
| Streak calculation looks back in linear time without a database index | For users with thousands of completion records, this could become slow |

## UI Limitations

| Limitation | Impact |
|---|---|
| No dark mode toggle | The design uses a light theme only |
| Not fully optimized for mobile screens | Some complex card layouts may overflow on small phones |
| No drag-and-drop task ordering | Tasks are sorted automatically, not manually |

## Security Limitations

| Limitation | Impact | Fix |
|---|---|---|
| SECRET_KEY is hardcoded in `settings.py` | If repo is public, the key is compromised | Move to `.env` file with `python-decouple` |
| No rate limiting on login | Vulnerable to brute force attacks | Add `django-axes` or similar |
| No HTTPS enforcement | Users on the same network can eavesdrop | Add SSL/TLS and `SECURE_*` settings |
| ALLOWED_HOSTS is empty | Only safe in development | Set proper hostnames for production |

## Scalability Limitations

- SQLite is single-file, not distributed — cannot be used with multiple servers
- No CDN for static files — CSS/JS served directly by Django dev server
- No pagination on task/habit/goal lists — very active users with 500+ tasks may have slow page loads

---

# SECTION 9 — LOGICAL ERROR CHECK

## ✅ Issue 1: Division by Zero in Goal Progress

**Where:** `models.py`, line 52 (`progress_percentage` property)

**Status:** HANDLED CORRECTLY
```python
return int((self.completed_tasks / total) * 100) if total > 0 else 0
```
If a goal has no tasks, it returns 0% safely.

---

## ✅ Issue 2: Division by Zero in Productivity Score

**Where:** `views.py` dashboard view, line 167

**Status:** HANDLED CORRECTLY
```python
task_score = (day_completed_tasks / day_total_tasks * 100) if day_total_tasks > 0 else 0
```

---

## ✅ Issue 3: Two Reflections On Same Day

**Where:** `models.py`, Reflection model

**Status:** HANDLED CORRECTLY
```python
unique_together = ('user', 'date')
```
The database enforces uniqueness. The view uses `update_or_create` so saving twice just updates the existing record.

---

## ⚠️ Issue 4: Task Driven Habit With No Remaining Tasks

**Where:** `views.py`, `update_task_driven_habit()` function

**Scenario:** User has a task-driven habit. All linked trackable tasks are deleted. What happens?

**Analysis:** When tasks are deleted, their `habit` FK is set to NULL (`SET_NULL`). The `update_task_driven_habit` function queries `Task.objects.filter(habit=habit, task_type='trackable')`. If no tasks remain, the queryset is empty, no average is calculated, and no update is performed — the habit's last known completion % remains from before.

**Risk:** The habit shows stale data from the last task update, even though no tasks are linked.

**Fix recommendation:** In `update_task_driven_habit`, add a check — if no trackable tasks exist, save 0% for today:
```python
if not tasks.exists():
    HabitCompletion.objects.update_or_create(
        habit=habit, date=today, defaults={'completion_percentage': 0}
    )
    return
```

---

## ✅ Issue 5: Data Isolation Between Users

**Where:** All views

**Status:** ALL VIEWS CORRECTLY FILTER BY USER

Every query uses `filter(user=request.user)` or `get_object_or_404(Model, id=..., user=request.user)`. There is no way for User A to read or modify User B's data. Admin views additionally filter by `is_superuser=False` to separate admin data from user data.

---

## ✅ Issue 6: Login Required on All Private Views

**Where:** All views except `register` and login

**Status:** ALL PRIVATE VIEWS USE `@login_required`

The `LOGIN_URL = 'login'` setting in `settings.py` ensures that any unauthenticated access redirects to the login page. Visiting `/tasks/`, `/habits/`, etc. without login safely redirects.

---

## ✅ Issue 7: Admin Routes Protected From Regular Users

**Where:** All `/admin-panel/` views

**Status:** PROTECTED CORRECTLY
```python
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
```
All admin views use both `@login_required` and `@admin_required`. A regular user visiting `/admin-panel/overview/` is immediately redirected to the dashboard.

---

## ⚠️ Issue 8: Report CSV Generation With No Data

**Where:** `views.py`, `generate_report()` function

**Scenario:** User selects a date range with no data and requests a CSV.

**Analysis:** The CSV is generated with only section headers but no data rows. The file downloads successfully but is essentially empty inside each section.

**Risk:** Low — this is expected behaviour, but a user might be confused by an empty CSV.

**Fix recommendation:** Return a readable message if all sections are empty, rather than a nearly-blank CSV file.

---

## ⚠️ Issue 9: Leaderboard Task Score Calculation

**Where:** `views.py`, `admin_leaderboard()` function, lines 1008-1012

**Current code:**
```python
tasks = Task.objects.filter(user=user, created_at__date__lte=day)
t_total = tasks.count()
if t_total > 0:
    t_completed = tasks.filter(status='Completed', created_at__date=day).count()
    taskScore = (t_completed / t_total) * 100
```

**Issue:** `t_total` counts all tasks created up to and including the day, but `t_completed` only counts tasks completed ON that specific day. This makes the denominator much larger than the numerator for historical days, artificially deflating the task score.

**Example:** User has 50 tasks total. On Day 30, they complete 2. Task score = 2/50 = 4% — but realistically completing 2 in one day is good.

**Fix recommendation:** Use the same date filter for both total and completed:
```python
tasks_due_that_day = Task.objects.filter(user=user, due_date=day)
t_total = tasks_due_that_day.count()
t_completed = tasks_due_that_day.filter(status='Completed').count()
```

---

## ✅ Issue 10: Passwords Are Properly Hashed

**Where:** `views.py`, `register()` function

**Status:** HANDLED CORRECTLY
```python
user.set_password(form.cleaned_data['password'])
```
Django's `set_password()` uses PBKDF2 hashing with a salt. Passwords are never stored in plain text.

---

## ✅ Issue 11: CSRF Protection on All Forms

**Where:** All forms in templates

**Status:** ALL FORMS INCLUDE `{% csrf_token %}`

Django's `CsrfViewMiddleware` is active (see `settings.py`) and all forms include the CSRF token. This prevents cross-site request forgery attacks.

---

## ✅ Issue 12: Form Validation — Start Date After Due Date

**Where:** `forms.py`, `TaskForm.clean()` method

**Status:** HANDLED CORRECTLY
```python
if start_date and due_date and start_date > due_date:
    self.add_error('start_date', "Start date cannot be later than the due date.")
```

---

## ✅ Issue 13: Task Type and Tracking Mode Locked After Creation

**Where:** `forms.py`, `TaskForm.__init__()` and `HabitForm.__init__()`

**Status:** HANDLED CORRECTLY
```python
if self.instance and self.instance.pk:
    self.fields['task_type'].disabled = True
```
Disabled fields are ignored on form submission in Django — the existing value is preserved regardless of what is submitted. This prevents any workaround through direct form POST manipulation.

---

## Summary of Issues Found

| # | Issue | Severity | Status |
|---|---|---|---|
| 1 | Goal progress division by zero | Low | ✅ Fixed |
| 2 | Task score division by zero | Low | ✅ Fixed |
| 3 | Duplicate daily reflection | Medium | ✅ Fixed |
| 4 | Task-driven habit stale data when tasks deleted | Medium | ⚠️ Needs Fix |
| 5 | User data isolation | High | ✅ Correct |
| 6 | Login required enforcement | High | ✅ Correct |
| 7 | Admin routes protection | High | ✅ Correct |
| 8 | Empty CSV report | Low | ⚠️ Minor |
| 9 | Leaderboard task score denominator mismatch | Medium | ⚠️ Needs Fix |
| 10 | Password hashing | High | ✅ Correct |
| 11 | CSRF protection | High | ✅ Correct |
| 12 | Date validation | Low | ✅ Fixed |
| 13 | Task type / tracking mode lock | Medium | ✅ Correct |

---

*End of LifeOS Project Documentation*

*Generated: March 2026*  
*Project: LifeOS — Personal Productivity Web App*  
*Stack: Django 6.0.3 / SQLite / Vanilla CSS / Chart.js*
