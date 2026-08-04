# LifeOS — Personal Productivity & Life Management System

LifeOS is a personal productivity web application built with Django to help users organize their goals, manage daily tasks, track habits, reflect on their progress, and improve their lifestyle through consistent routines and measurable results.

It is designed for students, professionals, freelancers, and anyone who wants to become more intentional about how they spend their time.

---

## Overview

LifeOS solves the common problem of losing focus and consistency by connecting:

- Goals ? Tasks ? Progress
- Habits ? Daily Logs ? Streaks
- Reflections ? Self-review ? Growth

Instead of being just another to-do app, LifeOS helps users build a complete productivity system where every action contributes to long-term personal growth.

---

## Features

- Goal tracking and progress management
- Simple and trackable tasks
- Habit tracking with multiple modes
- Daily streak tracking
- Productivity dashboard with charts
- Personal reflection and journaling system
- CSV report generation
- Admin analytics panel
- Secure authentication
- Responsive and user-friendly interface

---

## Why LifeOS?

Most people struggle with:

- forgetting long-term goals
- losing consistency in daily routines
- failing to measure progress
- not reflecting on their outcomes

LifeOS helps users:

- stay accountable
- build long-term habits
- measure personal productivity
- review progress regularly
- improve through data and reflection

---

## Tech Stack

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript
- Chart.js
- Bootstrap-inspired styling

---

## Project Structure

```bash
LifeOS/
¦
+-- lifeos_app/
¦   +-- models.py
¦   +-- views.py
¦   +-- forms.py
¦   +-- urls.py
¦   +-- templates/
¦
+-- lifeos_project/
¦   +-- settings.py
¦   +-- urls.py
¦   +-- wsgi.py
¦
+-- static/
¦   +-- css/
¦   +-- js/
¦   +-- images/
¦
+-- templates/
¦   +-- base.html
¦
+-- manage.py
+-- db.sqlite3
+-- run_tests.py
+-- setup_db.py
+-- LifeOS_Project_Documentation.md
+-- README.md
+-- .gitignore
+-- requirements.txt
```

---

## Installation

1. Clone the repository

```bash
git clone https://github.com/NobleSunil/LifeOS.git
cd LifeOS
```

2. Create a virtual environment

```bash
python -m venv venv
```

3. Activate the environment

For Windows:
```bash
venv\Scripts\activate
```

For macOS/Linux:
```bash
source venv/bin/activate
```

4. Install dependencies

```bash
pip install django
```

5. Apply migrations

```bash
python manage.py migrate
```

6. Run the development server

```bash
python manage.py runserver
```

7. Open the app

```bash
http://127.0.0.1:8000/
```

---

## Screenshots

### Home Page

![Home Page](https://via.placeholder.com/1200x700.png?text=LifeOS+Home+Page)

### Dashboard

![Dashboard](https://via.placeholder.com/1200x700.png?text=LifeOS+Dashboard)

### Goals Page

![Goals Page](https://via.placeholder.com/1200x700.png?text=LifeOS+Goals)

### Tasks Page

![Tasks Page](https://via.placeholder.com/1200x700.png?text=LifeOS+Tasks)

### Habits Page

![Habits Page](https://via.placeholder.com/1200x700.png?text=LifeOS+Habits)

### Reflection Journal

![Reflection Journal](https://via.placeholder.com/1200x700.png?text=LifeOS+Reflection)

### Reports Page

![Reports Page](https://via.placeholder.com/1200x700.png?text=LifeOS+Reports)

### Admin Panel

![Admin Panel](https://via.placeholder.com/1200x700.png?text=LifeOS+Admin+Panel)

---

## Core Modules

### Dashboard
Displays:
- today's tasks
- active goals
- habit summaries
- productivity chart
- user insights

### Goals
Create long-term targets and track progress over time.

### Tasks
Manage both:
- simple tasks
- progress-based trackable tasks

### Habits
Build routines with:
- manual logging
- streaks
- progress tracking
- task-driven updates

### Reflections
Write structured daily notes with:
- Wins
- Challenges
- Tomorrow's plan

### Reports
Generate CSV reports for tasks, goals, habits, and reflections.

### Admin Panel
Monitor:
- total users
- activity trends
- habit analytics
- consistency leaderboard
- age-group insights

---

## User Flow

1. Sign up or log in
2. Create goals
3. Add tasks and habits
4. Update progress daily
5. Write reflections
6. Review reports and improve consistency

---

## Admin Flow

Admins can access analytics to monitor:
- total users
- active users
- platform activity
- task and habit usage
- user consistency
- age-based engagement patterns

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a pull request

---

## License

This project is open-source and available for personal and educational use.

---

## Contact

- GitHub: NobleSunil
- Project: LifeOS
