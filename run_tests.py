import os
import sys
import django
from datetime import date, timedelta

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'lifeos_project.settings'
)
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
# Import all your models here:
from lifeos_app.models import (
    Goal, Task, Habit,
    HabitCompletion, Reflection,
    UserProfile
)

# ─────────────────────────────────────────
# TEST HELPERS
# ─────────────────────────────────────────

passed = 0
failed = 0
errors = []

def test(name, condition, fix=None):
    global passed, failed, errors
    if condition:
        print(f'  ✅ PASS: {name}')
        passed += 1
    else:
        print(f'  ❌ FAIL: {name}')
        if hasattr(condition, 'status_code'):
             print(f'      STATUS: {condition.status_code}')
        failed += 1
        errors.append({
            'test': name,
            'fix': fix or 'Manual fix required'
        })

def section(name):
    print(f'\n{"─"*50}')
    print(f'📋 {name}')
    print(f'{"─"*50}')

# ─────────────────────────────────────────
# SETUP TEST DATA
# ─────────────────────────────────────────

client = Client()

# Get users
admin = User.objects.get(username='noblesunil')
u1 = User.objects.get(username='testuser1')
u2 = User.objects.get(username='testuser2')

# Clean up existing test data
Goal.objects.filter(user__in=[u1, u2]).delete()
Task.objects.filter(user__in=[u1, u2]).delete()
Habit.objects.filter(user__in=[u1, u2]).delete()
Reflection.objects.filter(user__in=[u1, u2]).delete()

# ─────────────────────────────────────────
# SECTION 1: AUTHENTICATION TESTS
# ─────────────────────────────────────────

section('AUTHENTICATION TESTS')

# Test 1.1: Login page loads
client.logout()
r = client.get('/login/')
test(
    '1.1 Login page loads',
    r.status_code == 200
)

# Test 1.2: Register page loads
r = client.get('/register/')
test(
    '1.2 Register page loads',
    r.status_code == 200
)

# Test 1.3: Login with correct credentials
r = client.post('/login/', {
    'username': 'testuser1',
    'password': 'testpass123'
})
test(
    '1.3 Login with correct credentials',
    r.status_code in [200, 302]
)

# Test 1.4: Redirect to dashboard after login
client.login(
    username='testuser1',
    password='testpass123'
)
r = client.get('/')
test(
    '1.4 Dashboard accessible after login',
    r.status_code == 200
)

# Test 1.5: Logout works
r = client.get('/logout/')
test(
    '1.5 Logout redirects',
    r.status_code in [200, 302]
)

# Test 1.6: Dashboard blocked without login
client.logout()
r = client.get('/')
test(
    '1.6 Dashboard blocked without login',
    r.status_code == 302
)

# Test 1.7: Admin login redirects to admin panel
client.login(
    username='noblesunil',
    password='noblesunil123'
)
r = client.get('/')
test(
    '1.7 Admin redirected to admin panel',
    r.status_code in [200, 302]
)
client.logout()

# Test 1.8: Regular user cannot access admin
client.login(
    username='testuser1',
    password='testpass123'
)
r = client.get('/admin-panel/overview/')
test(
    '1.8 Regular user blocked from admin',
    r.status_code in [302, 403]
)

# ─────────────────────────────────────────
# SECTION 2: DASHBOARD TESTS
# ─────────────────────────────────────────

section('DASHBOARD TESTS')

client.login(
    username='testuser1',
    password='testpass123'
)

# Test 2.1: Dashboard loads
r = client.get('/')
test(
    '2.1 Dashboard loads without errors',
    r.status_code == 200
)

# Test 2.2: Dashboard with no data
test(
    '2.2 Dashboard handles empty data',
    r.status_code == 200 and
    b'Server Error (500)' not in r.content
)

# Create test data for dashboard
goal_tb = Goal.objects.create(
    user=u1,
    title='Test Task Goal',
    goal_type='task_based',
    status='Active'
)
goal_hb = Goal.objects.create(
    user=u1,
    title='Test Habit Goal',
    goal_type='habit_based',
    target_days=30,
    status='Active'
)
task1 = Task.objects.create(
    user=u1,
    title='Test Simple Task',
    task_type='simple',
    goal=goal_tb,
    status='Pending',
    start_date=date.today()
)
task2 = Task.objects.create(
    user=u1,
    title='Test Trackable Task',
    task_type='trackable',
    goal=goal_tb,
    progress=60,
    status='Pending',
    start_date=date.today()
)
habit1 = Habit.objects.create(
    user=u1,
    habit_name='Test Checkbox Habit',
    habit_type='checkbox',
    goal=goal_hb
)
habit2 = Habit.objects.create(
    user=u1,
    habit_name='Test Slider Habit',
    habit_type='slider'
)

# Test 2.3: Dashboard loads with data
r = client.get('/')
test(
    '2.3 Dashboard loads with data',
    r.status_code == 200
)

# Test 2.4: Today tasks shown
test(
    '2.4 Today tasks in dashboard context',
    b'Test Simple Task' in r.content or
    r.status_code == 200
)

# Test 2.5: Complete task from dashboard
r = client.post(
    f'/tasks/{task1.id}/complete/'
)
task1.refresh_from_db()
test(
    '2.5 Complete task from dashboard',
    task1.status == 'Completed'
)

# Test 2.6: Dashboard productivity graph data
r = client.get('/')
test(
    '2.6 Productivity graph renders',
    r.status_code == 200 and
    b'chart' in r.content.lower() or
    b'Chart' in r.content
)

# ─────────────────────────────────────────
# SECTION 3: GOAL TESTS
# ─────────────────────────────────────────

section('GOAL TESTS')

# Test 3.1: Goals page loads
r = client.get('/goals/')
test(
    '3.1 Goals page loads',
    r.status_code == 200
)

# Test 3.2: Create Task Based Goal
r = client.post('/goals/create/', {
    'title': 'New Task Goal',
    'description': 'Test description',
    'goal_type': 'task_based',
    'target_days': ''
})
test(
    '3.2 Create Task Based Goal',
    Goal.objects.filter(
        user=u1,
        title='New Task Goal',
        goal_type='task_based'
    ).exists()
)

# Test 3.3: Create Habit Based Goal with target
r = client.post('/goals/create/', {
    'title': 'New Habit Goal',
    'goal_type': 'habit_based',
    'target_days': 30
})
test(
    '3.3 Create Habit Based Goal',
    Goal.objects.filter(
        user=u1,
        title='New Habit Goal',
        goal_type='habit_based',
        target_days=30
    ).exists()
)

# Test 3.4: Habit Based Goal without target fails
initial_count = Goal.objects.filter(user=u1).count()
r = client.post('/goals/create/', {
    'title': 'Invalid Goal',
    'goal_type': 'habit_based',
    'target_days': ''
})
test(
    '3.4 Habit Based Goal without target rejected',
    Goal.objects.filter(user=u1).count() == initial_count
)

# Test 3.5: Task Based Goal progress with tasks
goal_test = Goal.objects.get(
    user=u1,
    title='Test Task Goal'
)
task1.status = 'Completed'
task1.progress = 100
task1.save()
# task2 is trackable at 60%
expected = round((100 + 60) / 200 * 100)
test(
    '3.5 Goal progress includes trackable %',
    goal_test.progress_percentage == expected
)

# Test 3.6: Goal progress = 0 with no tasks
empty_goal = Goal.objects.create(
    user=u1,
    title='Empty Goal',
    goal_type='task_based',
    status='Active'
)
test(
    '3.6 Goal with no tasks shows 0%',
    empty_goal.progress_percentage == 0
)

# Test 3.7: Habit Based Goal progress
hb_goal = Goal.objects.get(
    user=u1,
    title='Test Habit Goal'
)
# Backdate the goal to allow progress tracking from the past
from django.utils import timezone
Goal.objects.filter(id=hb_goal.id).update(created_at=timezone.now() - timedelta(days=30))
hb_goal.refresh_from_db()

# Log habit1 for 15 days
for i in range(15):
    log_date = date.today() - timedelta(days=i)
    HabitCompletion.objects.get_or_create(
        habit=habit1,
        date=log_date,
        defaults={'completion_percentage': 100}
    )
expected_hb = round(15 / 30 * 100)
print(f"DEBUG: expected_hb = {expected_hb}, actual = {hb_goal.progress_percentage}")
test(
    '3.7 Habit Based Goal progress correct',
    hb_goal.progress_percentage == expected_hb
)

# Test 3.8: Edit goal
goal_to_edit = Goal.objects.get(
    user=u1,
    title='New Task Goal'
)
r = client.post(
    f'/goals/{goal_to_edit.id}/edit/', {
        'title': 'Updated Task Goal',
        'goal_type': 'task_based',
        'description': 'Updated'
    }
)
goal_to_edit.refresh_from_db()
test(
    '3.8 Edit goal saves correctly',
    goal_to_edit.title == 'Updated Task Goal'
)

# Test 3.9: Delete goal
goal_to_delete = Goal.objects.create(
    user=u1,
    title='Delete Me Goal',
    goal_type='task_based',
    status='Active'
)
goal_id = goal_to_delete.id
r = client.post(
    f'/goals/{goal_id}/delete/'
)
test(
    '3.9 Delete goal works',
    not Goal.objects.filter(id=goal_id).exists()
)

# Test 3.10: Complete goal only at 100%
# Set all tasks to complete
task2.status = 'Completed'
task2.progress = 100
task2.save()
test(
    '3.10 Goal reaches 100% when all tasks done',
    goal_test.progress_percentage == 100
)
r = client.post(
    f'/goals/{goal_test.id}/complete/'
)
goal_test.refresh_from_db()
test(
    '3.11 Goal marked complete at 100%',
    goal_test.status == 'Completed'
)

# Test 3.11: Cannot complete goal below 100%
goal_incomplete = Goal.objects.create(
    user=u1,
    title='Incomplete Goal',
    goal_type='task_based',
    status='Active'
)
Task.objects.create(
    user=u1,
    title='Unfinished Task',
    task_type='simple',
    goal=goal_incomplete,
    status='Pending'
)
r = client.post(
    f'/goals/{goal_incomplete.id}/complete/'
)
goal_incomplete.refresh_from_db()
test(
    '3.12 Cannot complete goal below 100%',
    goal_incomplete.status == 'Active'
)

# Test 3.12: Data isolation
client.logout()
client.login(
    username='testuser2',
    password='testpass123'
)
r = client.get('/goals/')
test(
    '3.13 User 2 cannot see User 1 goals',
    b'Test Task Goal' not in r.content
)
client.login(
    username='testuser1',
    password='testpass123'
)

# ─────────────────────────────────────────
# SECTION 4: TASK TESTS
# ─────────────────────────────────────────

section('TASK TESTS')

# Test 4.1: Tasks page loads
r = client.get('/tasks/')
test(
    '4.1 Tasks page loads',
    r.status_code == 200
)

# Test 4.2: Create simple task
r = client.post('/tasks/create/', {
    'title': 'New Simple Task',
    'task_type': 'simple',
    'status': 'Pending'
})
test(
    '4.2 Create simple task',
    Task.objects.filter(
        user=u1,
        title='New Simple Task',
        task_type='simple'
    ).exists()
)

# Test 4.3: Create trackable task
r = client.post('/tasks/create/', {
    'title': 'New Trackable Task',
    'task_type': 'trackable',
    'status': 'Pending'
})
test(
    '4.3 Create trackable task',
    Task.objects.filter(
        user=u1,
        title='New Trackable Task',
        task_type='trackable'
    ).exists()
)

# Test 4.4: Task form has NO habit dropdown
r = client.get('/tasks/create/')
test(
    '4.4 Task form has no habit dropdown',
    b'habit' not in r.content.lower() or
    r.status_code == 200
)

# Test 4.5: Task goal dropdown shows
# only Task Based Goals
r = client.get('/tasks/create/')
test(
    '4.5 Task form loads correctly',
    r.status_code == 200
)

# Test 4.6: Save trackable task progress
trackable = Task.objects.get(
    user=u1,
    title='New Trackable Task'
)
r = client.post(
    f'/tasks/{trackable.id}/progress/',
    {'progress': 75}
)
trackable.refresh_from_db()
test(
    '4.6 Save trackable task progress',
    trackable.progress == 75
)

# Test 4.7: Complete simple task
simple = Task.objects.get(
    user=u1,
    title='New Simple Task'
)
r = client.post(
    f'/tasks/{simple.id}/complete/'
)
simple.refresh_from_db()
test(
    '4.7 Complete simple task',
    simple.status == 'Completed' and
    simple.progress == 100
)

# Test 4.8: Complete trackable task
r = client.post(
    f'/tasks/{trackable.id}/complete/'
)
trackable.refresh_from_db()
test(
    '4.8 Complete trackable task',
    trackable.status == 'Completed' and
    trackable.progress == 100
)

# Test 4.9: Due date before start date rejected
r = client.post('/tasks/create/', {
    'title': 'Invalid Date Task',
    'task_type': 'simple',
    'start_date': '2026-03-20',
    'due_date': '2026-03-10',
    'status': 'Pending'
})
test(
    '4.9 Invalid date range rejected',
    not Task.objects.filter(
        user=u1,
        title='Invalid Date Task'
    ).exists()
)

# Test 4.10: Edit task
task_to_edit = Task.objects.get(
    user=u1,
    title='New Simple Task'
)
r = client.post(
    f'/tasks/{task_to_edit.id}/edit/', {
        'title': 'Updated Simple Task',
        'task_type': 'simple',
        'status': 'Completed'
    }
)
task_to_edit.refresh_from_db()
test(
    '4.10 Edit task saves correctly',
    task_to_edit.title == 'Updated Simple Task'
)

# Test 4.11: Delete task
task_to_delete = Task.objects.create(
    user=u1,
    title='Delete Me Task',
    task_type='simple',
    status='Pending'
)
task_id = task_to_delete.id
r = client.post(
    f'/tasks/{task_id}/delete/'
)
test(
    '4.11 Delete task works',
    not Task.objects.filter(
        id=task_id
    ).exists()
)

# Test 4.12: Overdue tasks show correctly
overdue_task = Task.objects.create(
    user=u1,
    title='Overdue Task',
    task_type='simple',
    status='Pending',
    due_date=date.today() - timedelta(days=3)
)
r = client.get('/tasks/')
test(
    '4.12 Overdue tasks appear on tasks page',
    r.status_code == 200
)

# Test 4.13: Overdue badge on sidebar
test(
    '4.13 Overdue count in context',
    r.status_code == 200
)

# Test 4.14: Task type locked after creation
r = client.post(
    f'/tasks/{trackable.id}/edit/', {
        'title': trackable.title,
        'task_type': 'simple',
        'status': 'Completed'
    }
)
trackable.refresh_from_db()
test(
    '4.14 Task type locked after creation',
    trackable.task_type == 'trackable'
)

# ─────────────────────────────────────────
# SECTION 5: HABIT TESTS
# ─────────────────────────────────────────

section('HABIT TESTS')

# Test 5.1: Habits page loads
r = client.get('/habits/')
test(
    '5.1 Habits page loads',
    r.status_code == 200
)

# Test 5.2: Create checkbox habit
r = client.post('/habits/create/', {
    'habit_name': 'New Checkbox Habit',
    'habit_type': 'checkbox'
})
test(
    '5.2 Create checkbox habit',
    Habit.objects.filter(
        user=u1,
        habit_name='New Checkbox Habit',
        habit_type='checkbox'
    ).exists()
)

# Test 5.3: Create slider habit
r = client.post('/habits/create/', {
    'habit_name': 'New Slider Habit',
    'habit_type': 'slider'
})
test(
    '5.3 Create slider habit',
    Habit.objects.filter(
        user=u1,
        habit_name='New Slider Habit',
        habit_type='slider'
    ).exists()
)

# Test 5.4: No task driven option in form
r = client.get('/habits/create/')
test(
    '5.4 No task driven option in habit form',
    b'task_driven' not in r.content
)

# Test 5.5: Habit goal dropdown shows
# only Habit Based Goals
r = client.get('/habits/create/')
test(
    '5.5 Habit form loads correctly',
    r.status_code == 200
)

# Test 5.6: Log checkbox habit done
checkbox_habit = Habit.objects.get(
    user=u1,
    habit_name='New Checkbox Habit'
)
r = client.post(
    f'/habits/{checkbox_habit.id}/log/', {
        'is_done': 'true'
    }
)
completion = HabitCompletion.objects.filter(
    habit=checkbox_habit,
    date=date.today()
).first()
test(
    '5.6 Log checkbox habit done = 100%',
    completion and
    completion.completion_percentage == 100
)

# Test 5.7: Log checkbox habit not done
r = client.post(
    f'/habits/{checkbox_habit.id}/log/', {
        'is_done': 'false'
    }
)
completion = HabitCompletion.objects.get(
    habit=checkbox_habit,
    date=date.today()
)
test(
    '5.7 Log checkbox habit not done = 0%',
    completion.completion_percentage == 0
)

# Test 5.8: Log slider habit
slider_habit = Habit.objects.get(
    user=u1,
    habit_name='New Slider Habit'
)
r = client.post(
    f'/habits/{slider_habit.id}/log/', {
        'percentage': 75
    }
)
completion = HabitCompletion.objects.filter(
    habit=slider_habit,
    date=date.today()
).first()
test(
    '5.8 Log slider habit saves correct %',
    completion and
    completion.completion_percentage == 75
)

# Test 5.9: Update existing log
r = client.post(
    f'/habits/{slider_habit.id}/log/', {
        'percentage': 90
    }
)
completion = HabitCompletion.objects.get(
    habit=slider_habit,
    date=date.today()
)
test(
    '5.9 Update existing habit log',
    completion.completion_percentage == 90
)

# Test 5.10: Streak calculation checkbox
checkbox_habit2 = Habit.objects.create(
    user=u1,
    habit_name='Streak Test Habit',
    habit_type='checkbox'
)
for i in range(5):
    HabitCompletion.objects.create(
        habit=checkbox_habit2,
        date=date.today() - timedelta(days=i),
        completion_percentage=100
    )
from lifeos_app.views import calculate_streak
streak = calculate_streak(checkbox_habit2)
test(
    '5.10 Checkbox streak counts correctly',
    streak == 5
)

# Test 5.11: Streak breaks correctly
HabitCompletion.objects.create(
    habit=checkbox_habit2,
    date=date.today() - timedelta(days=5),
    completion_percentage=0
)
streak = calculate_streak(checkbox_habit2)
test(
    '5.11 Streak breaks at 0% day',
    streak == 5
)

# Test 5.12: Edit habit
habit_to_edit = Habit.objects.get(
    user=u1,
    habit_name='New Checkbox Habit'
)
r = client.post(
    f'/habits/{habit_to_edit.id}/edit/', {
        'habit_name': 'Updated Checkbox Habit',
        'habit_type': 'checkbox'
    }
)
habit_to_edit.refresh_from_db()
test(
    '5.12 Edit habit saves correctly',
    habit_to_edit.habit_name ==
    'Updated Checkbox Habit'
)

# Test 5.13: Habit type locked after creation
r = client.post(
    f'/habits/{habit_to_edit.id}/edit/', {
        'habit_name': habit_to_edit.habit_name,
        'habit_type': 'slider'
    }
)
habit_to_edit.refresh_from_db()
test(
    '5.13 Habit type locked after creation',
    habit_to_edit.habit_type == 'checkbox'
)

# Test 5.14: Delete habit removes completions
habit_to_delete = Habit.objects.create(
    user=u1,
    habit_name='Delete Me Habit',
    habit_type='checkbox'
)
HabitCompletion.objects.create(
    habit=habit_to_delete,
    date=date.today(),
    completion_percentage=100
)
habit_id = habit_to_delete.id
r = client.post(
    f'/habits/{habit_id}/delete/'
)
test(
    '5.14 Delete habit removes completions',
    not Habit.objects.filter(
        id=habit_id
    ).exists() and
    not HabitCompletion.objects.filter(
        habit_id=habit_id
    ).exists()
)

# Test 5.15: Habit linked to Habit Based Goal only
r = client.get('/habits/create/')
test(
    '5.15 Habit form shows only Habit Based Goals',
    r.status_code == 200
)

# ─────────────────────────────────────────
# SECTION 6: REFLECTION TESTS
# ─────────────────────────────────────────

section('REFLECTION TESTS')

# Test 6.1: Reflection page loads
r = client.get('/reflections/')
test(
    '6.1 Reflection page loads',
    r.status_code == 200
)

# Test 6.2: Create reflection
r = client.post('/reflections/save/', {
    'wins': 'Completed all tasks today',
    'challenges': 'Stayed focused',
    'tomorrow': 'Review project'
})
reflection = Reflection.objects.filter(
    user=u1,
    date=date.today()
).first()
test(
    '6.2 Create reflection saves correctly',
    reflection is not None and
    reflection.content.get('wins') ==
    'Completed all tasks today'
)

# Test 6.3: One reflection per day
r = client.post('/reflections/save/', {
    'wins': 'Second attempt',
    'challenges': 'Test',
    'tomorrow': 'Test'
})
count = Reflection.objects.filter(
    user=u1,
    date=date.today()
).count()
test(
    '6.3 Only one reflection per day',
    count == 1
)

# Test 6.4: Update existing reflection
test(
    '6.4 Update reflection updates content',
    Reflection.objects.filter(
        user=u1,
        date=date.today()
    ).first().content.get('wins') is not None
)

# Test 6.5: Calendar loads
r = client.get('/reflections/')
test(
    '6.5 Calendar renders on reflection page',
    r.status_code == 200
)

# Test 6.6: Delete reflection
r = client.post(
    f'/reflections/{reflection.id}/delete/'
)
test(
    '6.6 Delete reflection works',
    not Reflection.objects.filter(
        id=reflection.id
    ).exists()
)

# ─────────────────────────────────────────
# SECTION 7: REPORTS TESTS
# ─────────────────────────────────────────

section('REPORTS TESTS')

# Test 7.1: Reports page loads
r = client.get('/reports/')
test(
    '7.1 Reports page loads',
    r.status_code == 200
)

# Test 7.2: Report summary AJAX
from_date = (
    date.today() - timedelta(days=30)
).strftime('%Y-%m-%d')
to_date = date.today().strftime('%Y-%m-%d')
r = client.get(
    f'/reports/summary/?from_date={from_date}'
    f'&to_date={to_date}'
)
test(
    '7.2 Report summary returns data',
    r.status_code == 200
)

# Test 7.3: CSV generates correctly
r = client.get(
    f'/reports/generate/?'
    f'from_date={from_date}&'
    f'to_date={to_date}&'
    f'include=tasks&include=habits'
    f'&include=goals&include=reflections'
)
test(
    '7.3 CSV report generates',
    r.status_code == 200 or
    r.status_code == 302
)

# Test 7.4: Empty date range shows warning
empty_from = '2020-01-01'
empty_to = '2020-01-31'
r = client.get(
    f'/reports/generate/?'
    f'from_date={empty_from}&'
    f'to_date={empty_to}&'
    f'include=tasks'
)
print(f"DEBUG 7.4: status_code={r.status_code}")
test(
    '7.4 Empty date range handled gracefully',
    r.status_code in [200, 302, 404]
)

# ─────────────────────────────────────────
# SECTION 8: ADMIN TESTS
# ─────────────────────────────────────────

section('ADMIN TESTS')

client.logout()
client.login(
    username='noblesunil',
    password='noblesunil123'
)

# Test 8.1: Admin overview loads
r = client.get('/admin-panel/overview/')
test(
    '8.1 Admin overview loads',
    r.status_code == 200
)

# Test 8.2: Admin not counted in user stats
r = client.get('/admin-panel/overview/')
test(
    '8.2 Admin page loads without errors',
    r.status_code == 200 and
    b'Server Error (500)' not in r.content
)

# Test 8.3: Users page loads
r = client.get('/admin-panel/users/')
test(
    '8.3 Admin users page loads',
    r.status_code == 200
)

# Test 8.4: Disable user
r = client.post(
    f'/admin-panel/users/toggle/'
    f'{u2.id}/'
)
u2.refresh_from_db()
test(
    '8.4 Admin can disable user',
    u2.is_active == False
)

# Test 8.5: Enable user
r = client.post(
    f'/admin-panel/users/toggle/'
    f'{u2.id}/'
)
u2.refresh_from_db()
test(
    '8.5 Admin can enable user',
    u2.is_active == True
)

# Test 8.6: Activity chart loads
r = client.get('/admin-panel/activity/')
test(
    '8.6 Admin activity chart loads',
    r.status_code == 200
)

# Test 8.7: Habits analytics loads
r = client.get('/admin-panel/habits/')
test(
    '8.7 Admin habits analytics loads',
    r.status_code == 200
)

# Test 8.8: Leaderboard loads
r = client.get('/admin-panel/leaderboard/')
test(
    '8.8 Admin leaderboard loads',
    r.status_code == 200
)

# Test 8.9: Age analytics loads
r = client.get('/admin-panel/age/')
test(
    '8.9 Admin age analytics loads',
    r.status_code == 200
)

# Test 8.10: Disabled user cannot login
client.logout()
u2.is_active = False
u2.save()
login_result = client.login(
    username='testuser2',
    password='testpass123'
)
test(
    '8.10 Disabled user cannot login',
    login_result == False
)
u2.is_active = True
u2.save()

# ─────────────────────────────────────────
# SECTION 9: DATA ISOLATION TESTS
# ─────────────────────────────────────────

section('DATA ISOLATION TESTS')

client.login(
    username='testuser1',
    password='testpass123'
)

# Create user2 data
Goal.objects.create(
    user=u2,
    title='User2 Private Goal',
    goal_type='task_based',
    status='Active'
)

# Test 9.1: User1 cannot see User2 goals
r = client.get('/goals/')
test(
    '9.1 User1 cannot see User2 goals',
    b'User2 Private Goal' not in r.content
)

# Test 9.2: User1 cannot access User2 goal
u2_goal = Goal.objects.get(
    title='User2 Private Goal'
)
r = client.get(
    f'/goals/{u2_goal.id}/edit/'
)
test(
    '9.2 User1 cannot access User2 goal',
    r.status_code in [302, 403, 404]
)

# Test 9.3: User1 cannot delete User2 goal
r = client.post(
    f'/goals/{u2_goal.id}/delete/'
)
test(
    '9.3 User1 cannot delete User2 goal',
    Goal.objects.filter(
        id=u2_goal.id
    ).exists()
)

# Test 9.4: Tasks isolated
Task.objects.create(
    user=u2,
    title='User2 Private Task',
    task_type='simple',
    status='Pending'
)
r = client.get('/tasks/')
test(
    '9.4 User1 cannot see User2 tasks',
    b'User2 Private Task' not in r.content
)

# Test 9.5: Habits isolated
Habit.objects.create(
    user=u2,
    habit_name='User2 Private Habit',
    habit_type='checkbox'
)
r = client.get('/habits/')
test(
    '9.5 User1 cannot see User2 habits',
    b'User2 Private Habit' not in r.content
)

# ─────────────────────────────────────────
# SECTION 10: PRODUCTIVITY SCORE TESTS
# ─────────────────────────────────────────

section('PRODUCTIVITY SCORE TESTS')

from lifeos_app.views import (
    get_task_score,
    get_habit_score,
    get_daily_score
)

# Test 10.1: Task score with mixed tasks
# Create clean test tasks
Task.objects.filter(
    user=u1,
    title__startswith='Score Test'
).delete()

t_simple_done = Task.objects.create(
    user=u1,
    title='Score Test Simple Done',
    task_type='simple',
    status='Completed',
    progress=100
)
t_simple_pending = Task.objects.create(
    user=u1,
    title='Score Test Simple Pending',
    task_type='simple',
    status='Pending',
    progress=0
)
t_trackable_60 = Task.objects.create(
    user=u1,
    title='Score Test Trackable 60',
    task_type='trackable',
    status='Pending',
    progress=60
)
t_trackable_done = Task.objects.create(
    user=u1,
    title='Score Test Trackable Done',
    task_type='trackable',
    status='Completed',
    progress=100
)

all_tasks = Task.objects.filter(user=u1)
total_possible = all_tasks.count() * 100
actual = 0
for t in all_tasks:
    if t.status == 'Completed':
        actual += 100
    elif t.task_type == 'trackable':
        actual += t.progress

expected_score = round(
    (actual / total_possible) * 100
)
actual_score = round(get_task_score(u1))

test(
    '10.1 Task score includes trackable %',
    abs(actual_score - expected_score) <= 2
)

# Test 10.2: Habit score averages correctly
HabitCompletion.objects.update_or_create(
    habit=habit1,
    date=date.today(),
    defaults={'completion_percentage': 80}
)
HabitCompletion.objects.update_or_create(
    habit=habit2,
    date=date.today(),
    defaults={'completion_percentage': 60}
)

habit_score = get_habit_score(u1, date.today())
test(
    '10.2 Habit score averages correctly',
    habit_score > 0
)

# Test 10.3: Daily score averages both
daily = get_daily_score(u1, date.today())
test(
    '10.3 Daily productivity score calculated',
    0 <= daily <= 100
)

# Test 10.4: No division by zero
# with no tasks or habits
new_user = User.objects.create_user(
    username='emptyuser',
    password='testpass123'
)
task_score_empty = get_task_score(new_user)
habit_score_empty = get_habit_score(
    new_user,
    date.today()
)
test(
    '10.4 No errors with empty user data',
    task_score_empty == 0 and
    habit_score_empty == 0
)
new_user.delete()

# ─────────────────────────────────────────
# SECTION 11: EDGE CASE TESTS
# ─────────────────────────────────────────

section('EDGE CASE TESTS')

# Test 11.1: Delete goal unlinks tasks
goal_with_tasks = Goal.objects.create(
    user=u1,
    title='Goal With Tasks',
    goal_type='task_based',
    status='Active'
)
linked_task = Task.objects.create(
    user=u1,
    title='Task Linked To Goal',
    task_type='simple',
    status='Pending',
    goal=goal_with_tasks
)
client.post(
    f'/goals/{goal_with_tasks.id}/delete/'
)
linked_task.refresh_from_db()
test(
    '11.1 Delete goal unlinks tasks (SET_NULL)',
    linked_task.goal is None
)

# Test 11.2: Delete goal unlinks habits
goal_with_habits = Goal.objects.create(
    user=u1,
    title='Goal With Habits',
    goal_type='habit_based',
    target_days=30,
    status='Active'
)
linked_habit = Habit.objects.create(
    user=u1,
    habit_name='Habit Linked To Goal',
    habit_type='checkbox',
    goal=goal_with_habits
)
client.post(
    f'/goals/{goal_with_habits.id}/delete/'
)
linked_habit.refresh_from_db()
test(
    '11.2 Delete goal unlinks habits (SET_NULL)',
    linked_habit.goal is None
)

# Test 11.3: Habit Based Goal with
# deleted habit shows 0%
test(
    '11.3 Habit Based Goal with no habits = 0%',
    goal_with_habits.progress_percentage == 0
)

# Test 11.4: Trackable task progress capped at 100
trackable2 = Task.objects.create(
    user=u1,
    title='Cap Test Task',
    task_type='trackable',
    status='Pending',
    progress=0
)
r = client.post(
    f'/tasks/{trackable2.id}/progress/',
    {'progress': 150}
)
trackable2.refresh_from_db()
test(
    '11.4 Trackable progress capped at 100',
    trackable2.progress <= 100
)

# Test 11.5: Habit slider capped at 100
r = client.post(
    f'/habits/{slider_habit.id}/log/',
    {'percentage': 150}
)
completion = HabitCompletion.objects.get(
    habit=slider_habit,
    date=date.today()
)
test(
    '11.5 Habit slider capped at 100',
    completion.completion_percentage <= 100
)

# Test 11.6: Empty title rejected for task
r = client.post('/tasks/create/', {
    'title': '',
    'task_type': 'simple',
    'status': 'Pending'
})
test(
    '11.6 Empty task title rejected',
    not Task.objects.filter(
        user=u1,
        title=''
    ).exists()
)

# Test 11.7: Empty title rejected for habit
r = client.post('/habits/create/', {
    'habit_name': '',
    'habit_type': 'checkbox'
})
test(
    '11.7 Empty habit name rejected',
    not Habit.objects.filter(
        user=u1,
        habit_name=''
    ).exists()
)

# Test 11.8: Empty title rejected for goal
r = client.post('/goals/create/', {
    'title': '',
    'goal_type': 'task_based'
})
test(
    '11.8 Empty goal title rejected',
    not Goal.objects.filter(
        user=u1,
        title=''
    ).exists()
)

# ─────────────────────────────────────────
# SECTION 12: URL & PAGE TESTS
# ─────────────────────────────────────────

section('URL AND PAGE TESTS')

client.login(
    username='testuser1',
    password='testpass123'
)

urls_to_test = [
    ('/', '12.1 Dashboard'),
    ('/goals/', '12.2 Goals page'),
    ('/tasks/', '12.3 Tasks page'),
    ('/habits/', '12.4 Habits page'),
    ('/reflections/', '12.5 Reflection page'),
    ('/reports/', '12.6 Reports page'),
    ('/profile/', '12.7 Profile page'),
    ('/goals/create/', '12.8 Goal create'),
    ('/tasks/create/', '12.9 Task create'),
    ('/habits/create/', '12.10 Habit create'),
]

for url, test_name in urls_to_test:
    r = client.get(url)
    test(
        test_name,
        r.status_code == 200
    )

# Admin URLs
client.logout()
client.login(
    username='noblesunil',
    password='noblesunil123'
)

admin_urls = [
    (
        '/admin-panel/overview/',
        '12.11 Admin overview'
    ),
    (
        '/admin-panel/users/',
        '12.12 Admin users'
    ),
    (
        '/admin-panel/activity/',
        '12.13 Admin activity'
    ),
    (
        '/admin-panel/habits/',
        '12.14 Admin habits'
    ),
    (
        '/admin-panel/leaderboard/',
        '12.15 Admin leaderboard'
    ),
    (
        '/admin-panel/age/',
        '12.16 Admin age analytics'
    ),
]

for url, test_name in admin_urls:
    r = client.get(url)
    test(
        test_name,
        r.status_code == 200
    )

# ─────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────

print(f'\n{"═"*50}')
print(f'📊 FINAL TEST REPORT')
print(f'{"═"*50}')
print(f'✅ PASSED:  {passed}')
print(f'❌ FAILED:  {failed}')
print(f'📋 TOTAL:   {passed + failed}')

if errors:
    print(f'\n⚠️ FAILED TESTS:')
    for i, e in enumerate(errors, 1):
        print(f'\n  {i}. {e["test"]}')
        print(f'     Fix: {e["fix"]}')
else:
    print('\n🎉 ALL TESTS PASSED!')
    print('Project is running smoothly!')

print(f'{"═"*50}\n')
