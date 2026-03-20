import csv
import json
import datetime
import calendar
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count, Q, Avg
from .forms import UserRegistrationForm, GoalForm, HabitForm, TaskForm, ReflectionForm, UserProfileForm
from .models import Goal, Task, Habit, HabitCompletion, Reflection, UserProfile

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            age = form.cleaned_data.get('age')
            UserProfile.objects.create(user=user, age=age)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        # Redirect admins to the admin dashboard, others to regular dashboard
        if self.request.user.is_superuser:
            return '/admin-panel/overview/'
        return super().get_success_url()

def get_habit_streak(habit, today):
    # Retrieve all completions for this habit ordered backwards
    completions = HabitCompletion.objects.filter(
        habit=habit, date__lte=today, completion_percentage__gt=0
    ).order_by('-date')
    
    streak = 0
    current_date = today
    
    # Check if today is completed
    today_completed = completions.filter(date=today).exists()
    
    # If not completed today, we might still have a streak ending yesterday
    if not today_completed:
        current_date = today - datetime.timedelta(days=1)
        
    for comp in completions:
        if comp.date == current_date:
            streak += 1
            current_date -= datetime.timedelta(days=1)
        elif comp.date < current_date:
            break
            
    return streak

@login_required
def dashboard(request):
    user = request.user
    today = datetime.date.today()
    current_hour = datetime.datetime.now().hour
    
    # --- Greeting Logic ---
    if 5 <= current_hour < 12:
        greeting_time = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting_time = "Good Afternoon"
    else:
        greeting_time = "Good Evening"

    try:
        display_name = user.userprofile.full_name.split()[0] if user.userprofile.full_name else user.username
    except UserProfile.DoesNotExist:
        display_name = user.username
        
    quotes = [
        "Focus on being productive instead of busy.",
        "Small steps every day lead to big results.",
        "Your future is created by what you do today, not tomorrow.",
        "Don't count the days, make the days count.",
        "Success is sum of small efforts repeated day in and day out.",
        "Action is the foundational key to all success.",
        "The secret of getting ahead is getting started."
    ]
    daily_quote = quotes[today.toordinal() % len(quotes)]
    
    # --- Quick Stats ---
    total_tasks_due_today = Task.objects.filter(user=user, start_date__lte=today, status='Pending').count()
    total_active_goals = Goal.objects.filter(user=user, status='Active').count()
    habits_logged_today = HabitCompletion.objects.filter(habit__user=user, date=today).values('habit').distinct().count()
    
    # --- Today's Tasks (Sorted) ---
    raw_today_tasks = list(Task.objects.filter(user=user, start_date__lte=today, status='Pending'))
    def sort_key(t):
        if t.due_date:
            if t.due_date < today: return 0  # Overdue
            elif t.due_date == today: return 1  # Due today
            else: return 2  # Future
        return 3  # No due date
        
    today_tasks = sorted(raw_today_tasks, key=sort_key)
    
    for t in today_tasks:
        if t.due_date:
            delta = (today - t.due_date).days
            if delta > 0:
                t.date_label = f"{delta} day{'s' if delta > 1 else ''} overdue"
                t.ui_status = "overdue"
            elif delta == 0:
                t.date_label = "Due today"
                t.ui_status = "today"
            else:
                t.date_label = f"Due in {abs(delta)} day{'s' if abs(delta) > 1 else ''}"
                t.ui_status = "future"
        else:
            t.date_label = "No due date"
            t.ui_status = "none"
            
    # --- Goal Progress ---
    active_goals = Goal.objects.filter(user=user, status='Active')
    for g in active_goals:
        total = g.tasks.count()
        completed = g.tasks.filter(status='Completed').count()
        g.progress_pct = (completed / total * 100) if total > 0 else 0
        g.completed_count = completed
        g.total_count = total
        
        if g.progress_pct <= 30: g.progress_color = 'danger'
        elif g.progress_pct <= 70: g.progress_color = 'warning'
        else: g.progress_color = 'success'

    # --- Today's Habits ---
    today_habits = Habit.objects.filter(user=user)
    for h in today_habits:
        completion = HabitCompletion.objects.filter(habit=h, date=today).first()
        h.completion_today = completion.completion_percentage if completion else None
        h.streak = get_habit_streak(h, today)
        
        pct = h.completion_today or 0
        if pct == 0: h.progress_color = 'secondary'
        elif pct <= 29: h.progress_color = 'danger'
        elif pct <= 69: h.progress_color = 'warning'
        else: h.progress_color = 'success'
        
    # --- Productivity Graph ---
    last_7_days = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
    chart_labels = [d.strftime('%a') for d in last_7_days]
    chart_data = []
    
    all_zeroes = True
    for d in last_7_days:
        day_avg_query = HabitCompletion.objects.filter(habit__user=user, date=d).aggregate(Avg('completion_percentage'))
        habit_score = day_avg_query['completion_percentage__avg'] or 0
        
        day_total_tasks = Task.objects.filter(user=user, due_date=d).count()
        day_completed_tasks = Task.objects.filter(user=user, due_date=d, status='Completed').count()
        task_score = (day_completed_tasks / day_total_tasks * 100) if day_total_tasks > 0 else 0
        
        productivity_score = round((habit_score + task_score) / 2)
        chart_data.append(productivity_score)
        if productivity_score > 0:
            all_zeroes = False
            
    has_activity_data = not all_zeroes
    avg_score = round(sum(chart_data) / len(chart_data)) if chart_data else 0
    
    context = {
        'greeting_time': greeting_time,
        'display_name': display_name,
        'today_date': today,
        'daily_quote': daily_quote,
        'total_tasks_due_today': total_tasks_due_today,
        'total_active_goals': total_active_goals,
        'habits_logged_today': habits_logged_today,
        'today_tasks': today_tasks,
        'active_goals': active_goals,
        'today_habits': today_habits,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'has_activity_data': has_activity_data,
        'avg_score': avg_score,
    }
    
    return render(request, 'dashboard.html', context)

# ==================== PROFILE ====================
@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user_obj=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = UserProfileForm(instance=profile, user_obj=request.user)
        
    return render(request, 'profile.html', {'form': form, 'profile': profile})

# ==================== GOALS ====================
@login_required
def goals_list(request):
    goals = Goal.objects.filter(user=request.user).order_by('-created_at')
    
    for g in goals:
        total = g.tasks.count()
        completed = g.tasks.filter(status='Completed').count()
        g.task_count = total          # renamed to avoid clashing with Goal @property
        g.done_count = completed      # renamed to avoid clashing with Goal @property
        g.habit_count = g.habits.count()
        
        if total == 0:
            g.progress = 0
        else:
            g.progress = (completed / total) * 100
            
        if g.progress <= 30:
            g.progress_color = 'danger'
        elif g.progress <= 70:
            g.progress_color = 'warning'
        elif g.progress <= 99:
            g.progress_color = 'primary'
        else:
            g.progress_color = 'success'

    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            g = form.save(commit=False)
            g.user = request.user
            g.save()
            return redirect('goals_list')
    else:
        form = GoalForm()
    return render(request, 'goals.html', {'goals': goals, 'form': form})

@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    goal.delete()
    return redirect('goals_list')

@login_required
def complete_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    goal.status = 'Completed'
    goal.completed_at = timezone.now()
    goal.save()
    return redirect('goals_list')

@login_required
def edit_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('goals_list')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'edit_goal.html', {'form': form, 'goal': goal})

# ==================== HABITS ====================
def calculate_streak(habit):
    """Calculate streak based on tracking mode:
    - manual_checkbox: counts consecutive days with percentage == 100
    - manual_slider / task_driven: counts consecutive days with percentage > 0
    """
    today = datetime.date.today()
    streak = 0
    current_date = today

    while True:
        completion = HabitCompletion.objects.filter(
            habit=habit,
            date=current_date
        ).first()

        if habit.tracking_mode == 'manual_checkbox':
            completed = completion and completion.completion_percentage == 100
        else:
            completed = completion and completion.completion_percentage > 0

        if completed:
            streak += 1
            current_date -= datetime.timedelta(days=1)
        else:
            break

    return streak

def get_weekly_data(habit):
    today = datetime.date.today()
    weekly_data = []

    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        completion = HabitCompletion.objects.filter(
            habit=habit,
            date=day
        ).first()

        weekly_data.append({
            'day': day.strftime('%a'),
            'percentage': completion.completion_percentage if completion else 0,
            'logged': completion is not None,  # whether any record exists for this day
        })

    return weekly_data

@login_required
def habits_list(request):
    user = request.user
    habits = Habit.objects.filter(user=user).order_by('-created_at')
    today = datetime.date.today()
    
    user_goals = Goal.objects.filter(user=user, status='Active')
    
    for habit in habits:
        completion = HabitCompletion.objects.filter(habit=habit, date=today).first()
        habit.completion_percentage_today = completion.completion_percentage if completion else 0
        habit.current_streak = calculate_streak(habit)
        habit.weekly_data = get_weekly_data(habit)
        habit.linked_tasks = habit.tasks.all()
        # For task-driven habits: only show trackable tasks
        habit.linked_trackable_tasks = habit.tasks.filter(task_type='trackable')

    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            h = form.save(commit=False)
            h.user = user
            h.save()
            return redirect('habits_list')
    else:
        form = HabitForm()
        
    context = {
        'habits': habits,
        'user_goals': user_goals,
        'form': form
    }
    return render(request, 'habits.html', context)

@login_required
def edit_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            return redirect('habits_list')
    return redirect('habits_list')

@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    habit.delete()  # Cascade deletes HabitCompletions automatically
    return redirect('habits_list')

@login_required
def complete_habit(request, habit_id):
    """Legacy URL handler — delegates to save_habit_log for back-compat."""
    return save_habit_log(request, habit_id)

@login_required
def save_habit_log(request, habit_id):
    """Save habit completion log. Behavior differs by tracking_mode."""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    today = datetime.date.today()
    if request.method == 'POST':
        if habit.tracking_mode == 'manual_slider':
            try:
                percentage = int(request.POST.get('percentage', 0))
                percentage = max(0, min(100, percentage))
            except (ValueError, TypeError):
                percentage = 0

        elif habit.tracking_mode == 'manual_checkbox':
            is_done = request.POST.get('is_done') == 'true'
            percentage = 100 if is_done else 0

        elif habit.tracking_mode == 'task_driven':
            # task-driven habits cannot be manually logged
            return redirect('habits_list')
        else:
            percentage = 0

        HabitCompletion.objects.update_or_create(
            habit=habit,
            date=today,
            defaults={'completion_percentage': percentage}
        )
    return redirect('habits_list')

# ==================== TASKS ====================

def update_task_driven_habit(habit):
    """Recalculate task-driven habit completion % as average of linked trackable task progress."""
    trackable_tasks = Task.objects.filter(habit=habit, task_type='trackable')
    if not trackable_tasks.exists():
        return
    avg = sum(t.progress for t in trackable_tasks) / trackable_tasks.count()
    HabitCompletion.objects.update_or_create(
        habit=habit,
        date=datetime.date.today(),
        defaults={'completion_percentage': round(avg)}
    )


@login_required
def tasks_list(request):
    user = request.user
    today = datetime.date.today()
    all_tasks = Task.objects.filter(user=user)
    
    # 1. Overdue
    overdue_tasks = all_tasks.filter(due_date__lt=today, status='Pending').order_by('due_date')
    
    # 2. Today
    today_tasks = all_tasks.filter(start_date__lte=today, status='Pending', due_date=today).order_by('created_at')
    
    # 3. Pending
    raw_pending = all_tasks.filter(status='Pending').exclude(id__in=overdue_tasks).exclude(id__in=today_tasks)
    pending_tasks = sorted(raw_pending, key=lambda t: (t.due_date is None, t.due_date))
    
    # 4. Completed
    completed_tasks = all_tasks.filter(status='Completed')
    
    # Process Labels
    all_processed = list(overdue_tasks) + list(today_tasks) + list(pending_tasks) + list(completed_tasks)
    for task in all_processed:
        if task.due_date:
            delta = (task.due_date - today).days
            if delta < 0:
                task.due_label = f"{abs(delta)} day{'s' if abs(delta) > 1 else ''} overdue"
                task.due_color = 'danger'
            elif delta == 0:
                task.due_label = "Due today"
                task.due_color = 'warning'
            else:
                task.due_label = f"Due in {delta} day{'s' if delta > 1 else ''}"
                task.due_color = 'text-primary'
        else:
            task.due_label = "No due date"
            task.due_color = 'secondary'
            
    # For Dropdowns
    user_goals = Goal.objects.filter(user=user, status='Active')
    for g in user_goals:
        total = g.tasks.count()
        completed = g.tasks.filter(status='Completed').count()
        g.is_100_percent = (total > 0 and total == completed)
        
    user_habits = Habit.objects.filter(user=user)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.user = user
            t.save()
            return redirect('tasks_list')
    else:
        form = TaskForm()
        
    context = {
        'overdue_tasks': overdue_tasks,
        'today_tasks': today_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'user_goals': user_goals,
        'user_habits': user_habits,
        'form': form
    }
    return render(request, 'tasks.html', context)

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect('tasks_list')

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.status = 'Completed'
    task.progress = 100  # completing always sets progress to 100
    task.save()
    # if linked to a task-driven habit, recalculate it
    if task.habit and task.habit.tracking_mode == 'task_driven':
        update_task_driven_habit(task.habit)
    return redirect('tasks_list')

@login_required
def save_task_progress(request, task_id):
    """Save progress % for a trackable task and recalculate any linked task-driven habit."""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user, task_type='trackable')
        try:
            progress = int(request.POST.get('progress', 0))
            progress = max(0, min(100, progress))
        except (ValueError, TypeError):
            progress = 0
        task.progress = progress
        task.save()
        # recalculate linked task-driven habit if any
        if task.habit and task.habit.tracking_mode == 'task_driven':
            update_task_driven_habit(task.habit)
    return redirect('tasks_list')

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'edit_task.html', {'form': form, 'task': task})

# ==================== REFLECTIONS ====================
def calculate_reflection_streak(user):
    today = datetime.date.today()
    streak = 0
    current_date = today

    while True:
        exists = Reflection.objects.filter(
            user=user,
            date=current_date
        ).exists()

        if exists:
            streak += 1
            current_date -= datetime.timedelta(days=1)
        else:
            break

    return streak

@login_required
def reflections_list(request):
    user = request.user
    today = datetime.date.today()
    
    # Handle Save
    if request.method == 'POST':
        wins = request.POST.get('wins', '')
        challenges = request.POST.get('challenges', '')
        tomorrow = request.POST.get('tomorrow', '')
        
        # At least one field must be filled
        if wins or challenges or tomorrow:
            content = {
                'wins': wins,
                'challenges': challenges,
                'tomorrow': tomorrow
            }
            Reflection.objects.update_or_create(
                user=user,
                date=today,
                defaults={'content': content}
            )
        return redirect('reflections_list')

    # Get Calendar Query Context
    try:
        current_year = int(request.GET.get('year', today.year))
        current_month = int(request.GET.get('month', today.month))
    except ValueError:
        current_year = today.year
        current_month = today.month

    # Bounding checks
    user_joined_date = user.date_joined.date()
    
    # Prevent future navigation
    if current_year > today.year or (current_year == today.year and current_month > today.month):
        current_year = today.year
        current_month = today.month
        
    # Generate Calendar Grid
    raw_cal = calendar.monthcalendar(current_year, current_month)
    
    # Get Reflections for this month
    monthly_reflections = Reflection.objects.filter(
        user=user,
        date__year=current_year,
        date__month=current_month
    )
    
    # Pack for Frontend
    reflection_dates_str = [r.date.strftime('%Y-%m-%d') for r in monthly_reflections]
    
    cal_data = []
    for week in raw_cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': 0, 'date_str': ''})
            else:
                date_str = f"{current_year}-{current_month:02d}-{day:02d}"
                week_data.append({
                    'day': day,
                    'date_str': date_str,
                    'has_reflection': date_str in reflection_dates_str,
                    'is_today': date_str == today.strftime('%Y-%m-%d')
                })
        cal_data.append(week_data)
    
    reflections_dict = {}
    for r in monthly_reflections:
        reflections_dict[r.date.strftime('%Y-%m-%d')] = {
            'id': r.id,
            'wins': r.content.get('wins', ''),
            'challenges': r.content.get('challenges', ''),
            'tomorrow': r.content.get('tomorrow', '')
        }
        
    # Navigation Math
    prev_month = current_month - 1
    prev_year = current_year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
        
    next_month = current_month + 1
    next_year = current_year
    if next_month == 13:
        next_month = 1
        next_year += 1
        
    # Disable Previous if goes before user Registration
    disable_prev = False
    if prev_year < user_joined_date.year or (prev_year == user_joined_date.year and prev_month < user_joined_date.month):
        disable_prev = True
        
    disable_next = False
    if next_year > today.year or (next_year == today.year and next_month > today.month):
        disable_next = True
        
    streak = calculate_reflection_streak(user)
    total_empty = Reflection.objects.filter(user=user).count() == 0

    # Get today's reflection ID if it exists (for the cancel button)
    today_reflection = Reflection.objects.filter(user=user, date=today).first()
    today_reflection_id = today_reflection.id if today_reflection else None

    context = {
        'today_str': today.strftime('%Y-%m-%d'),
        'current_month_name': calendar.month_name[current_month],
        'current_year': current_year,
        'current_month': current_month,
        'cal': cal_data,
        'reflection_dates_str': reflection_dates_str,
        'reflections_json': json.dumps(reflections_dict),
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'disable_prev': disable_prev,
        'disable_next': disable_next,
        'streak': streak,
        'total_empty': total_empty,
        'today_reflection_id': today_reflection_id,
    }
    
    return render(request, 'reflections.html', context)

@login_required
def delete_reflection(request, reflection_id):
    reflection = get_object_or_404(Reflection, id=reflection_id, user=request.user)
    if request.method == 'POST':
        reflection.delete()
    return redirect('reflections_list')

@login_required
def edit_reflection(request, reflection_id):
    reflection = get_object_or_404(Reflection, id=reflection_id, user=request.user)
    if request.method == 'POST':
        form = ReflectionForm(request.POST, instance=reflection)
        if form.is_valid():
            form.save()
            return redirect('reflections_list')
    else:
        form = ReflectionForm(instance=reflection)
    return render(request, 'edit_reflection.html', {'form': form, 'reflection': reflection})

# ==================== REPORTS ====================

def get_report_summary(user, from_date, to_date):
    summary = {}
    summary['tasks'] = Task.objects.filter(
        user=user, created_at__date__gte=from_date, created_at__date__lte=to_date
    ).count()
    summary['habits'] = HabitCompletion.objects.filter(
        habit__user=user, date__gte=from_date, date__lte=to_date
    ).count()
    summary['goals'] = Goal.objects.filter(
        user=user, created_at__date__gte=from_date, created_at__date__lte=to_date
    ).count()
    summary['reflections'] = Reflection.objects.filter(
        user=user, date__gte=from_date, date__lte=to_date
    ).count()
    summary['total'] = sum(summary.values())
    return summary

@login_required
def report_summary_api(request):
    try:
        from_date_str = request.GET.get('from_date')
        to_date_str = request.GET.get('to_date')
        if not from_date_str or not to_date_str:
            return JsonResponse({'error': 'Missing dates'}, status=400)
            
        from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date()
        summary = get_report_summary(request.user, from_date, to_date)
        return JsonResponse(summary)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def reports_page(request):
    min_date = request.user.date_joined.date().strftime('%Y-%m-%d')
    today = datetime.date.today().strftime('%Y-%m-%d')
    return render(request, 'reports.html', {'min_date': min_date, 'today': today})

@login_required
def generate_report(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    include = request.GET.getlist('include')

    response = HttpResponse(content_type='text/csv')
    filename = f'LifeOS_Report_{from_date}_to_{to_date}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    # TASKS SECTION
    if 'tasks' in include:
        writer.writerow(['==== TASKS ===='])
        writer.writerow([
            'Title', 'Description', 'Status', 'Start Date', 'Due Date', 'Linked Goal', 'Linked Habit', 'Created At'
        ])
        tasks = Task.objects.filter(
            user=request.user, created_at__date__gte=from_date, created_at__date__lte=to_date
        )
        for task in tasks:
            writer.writerow([
                task.title,
                task.description or '',
                task.status,
                task.start_date or '',
                task.due_date or '',
                task.goal.title if task.goal else '',
                task.habit.habit_name if task.habit else '',
                task.created_at.strftime('%Y-%m-%d')
            ])
        writer.writerow([])

    # HABITS SECTION
    if 'habits' in include:
        writer.writerow(['==== HABITS ===='])
        writer.writerow(['Habit Name', 'Linked Goal', 'Date', 'Completion %'])
        completions = HabitCompletion.objects.filter(
            habit__user=request.user, date__gte=from_date, date__lte=to_date
        ).select_related('habit')
        for completion in completions:
            writer.writerow([
                completion.habit.habit_name,
                completion.habit.goal.title if completion.habit.goal else '',
                completion.date,
                completion.completion_percentage
            ])
        writer.writerow([])

    # GOALS SECTION
    if 'goals' in include:
        writer.writerow(['==== GOALS ===='])
        writer.writerow(['Title', 'Description', 'Status', 'Progress %', 'Tasks Linked', 'Habits Linked', 'Created At'])
        goals = Goal.objects.filter(
            user=request.user, created_at__date__gte=from_date, created_at__date__lte=to_date
        )
        for goal in goals:
            total = Task.objects.filter(goal=goal).count()
            completed = Task.objects.filter(goal=goal, status='Completed').count()
            progress = (completed / total * 100) if total > 0 else 0
            habits_linked = Habit.objects.filter(goal=goal).count()
            writer.writerow([
                goal.title,
                goal.description or '',
                goal.status,
                f'{progress:.0f}%',
                total,
                habits_linked,
                goal.created_at.strftime('%Y-%m-%d')
            ])
        writer.writerow([])

    # REFLECTIONS SECTION
    if 'reflections' in include:
        writer.writerow(['==== REFLECTIONS ===='])
        writer.writerow(['Date', 'Wins', 'Challenges', "Tomorrow's Plan"])
        reflections = Reflection.objects.filter(
            user=request.user, date__gte=from_date, date__lte=to_date
        )
        for reflection in reflections:
            writer.writerow([
                reflection.date,
                reflection.content.get('wins', ''),
                reflection.content.get('challenges', ''),
                reflection.content.get('tomorrow', '')
            ])

    return response

# ==================== ADMIN DASHBOARD ====================

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@admin_required
def admin_dashboard_overview(request):
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=7)

    total_users = User.objects.filter(is_superuser=False).count()

    active_users = User.objects.filter(
        is_superuser=False,
        is_active=True,
    ).filter(
        Q(task__created_at__date__gte=seven_days_ago) |
        Q(habit__habitcompletion__date__gte=seven_days_ago) |
        Q(reflection__date__gte=seven_days_ago)
    ).distinct().count()

    total_goals = Goal.objects.filter(user__is_superuser=False).count()
    total_tasks = Task.objects.filter(user__is_superuser=False).count()
    total_habits = Habit.objects.filter(user__is_superuser=False).count()

    all_completions = HabitCompletion.objects.filter(habit__user__is_superuser=False)
    if all_completions.exists():
        habit_completion_rate = all_completions.aggregate(avg=Avg('completion_percentage'))['avg']
    else:
        habit_completion_rate = 0

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'total_goals': total_goals,
        'total_tasks': total_tasks,
        'total_habits': total_habits,
        'habit_completion_rate': round(habit_completion_rate),
    }
    return render(request, 'admin_overview.html', context)

@login_required
@admin_required
def admin_users(request):
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    
    search_query = request.GET.get('q', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    filter_status = request.GET.get('status', 'all')
    if filter_status == 'active':
        users = users.filter(is_active=True)
    elif filter_status == 'inactive':
        users = users.filter(is_active=False)
        
    context = {
        'users': users,
        'search_query': search_query,
        'filter_status': filter_status,
    }
    return render(request, 'admin_users.html', context)

@login_required
@admin_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    user.is_active = not user.is_active
    user.save()
    return redirect('admin_users')

@login_required
@admin_required
def admin_activity(request):
    today = datetime.date.today()
    activity_data = []

    for i in range(29, -1, -1):
        day = today - datetime.timedelta(days=i)

        tasks_completed = Task.objects.filter(
            user__is_superuser=False,
            status='Completed',
            created_at__date=day
        ).count()

        habits_logged = HabitCompletion.objects.filter(
            habit__user__is_superuser=False,
            date=day,
            completion_percentage__gt=0
        ).count()

        activity_data.append({
            'date': day.strftime('%b %d'),
            'score': tasks_completed + habits_logged
        })

    context = {
        'activity_data_json': json.dumps(activity_data),
        'total_activity_period': sum(item['score'] for item in activity_data)
    }
    return render(request, 'admin_activity.html', context)

@login_required
@admin_required
def admin_habits(request):
    top_habits = Habit.objects.filter(
        user__is_superuser=False
    ).values('habit_name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    top_users = User.objects.filter(
        is_superuser=False
    ).annotate(
        log_count=Count('habit__habitcompletion')
    ).order_by('-log_count')[:5]

    context = {
        'top_habits': top_habits,
        'top_users': top_users,
    }
    return render(request, 'admin_habits.html', context)

@login_required
@admin_required
def admin_leaderboard(request):
    users = User.objects.filter(is_superuser=False)
    leaderboard = []

    def get_last_n_active_days(user, n):
        task_dates = list(Task.objects.filter(
            user=user, status='Completed'
        ).dates('created_at', 'day'))
        
        habit_dates = list(HabitCompletion.objects.filter(
            habit__user=user, completion_percentage__gt=0
        ).values_list('date', flat=True).distinct())
        
        all_dates = sorted(list(set(task_dates + habit_dates)), reverse=True)
        return all_dates[:n]

    for user in users:
        task_days = Task.objects.filter(
            user=user,
            status='Completed'
        ).dates('created_at', 'day').count()

        habit_days = HabitCompletion.objects.filter(
            habit__user=user,
            completion_percentage__gt=0
        ).values('date').distinct().count()

        active_days = max(task_days, habit_days)

        if active_days < 5:
            continue
            
        scores = []
        for day in get_last_n_active_days(user, active_days):
            habitScore = 0
            hab_comps = HabitCompletion.objects.filter(habit__user=user, date=day)
            h_count = hab_comps.count()
            if h_count > 0:
                habitScore = sum(hc.completion_percentage for hc in hab_comps) / h_count
                
            taskScore = 0
            tasks = Task.objects.filter(user=user, created_at__date__lte=day)
            t_total = tasks.count()
            if t_total > 0:
                t_completed = tasks.filter(status='Completed', created_at__date=day).count()
                taskScore = (t_completed / t_total) * 100
                
            scores.append((habitScore + taskScore) / 2)

        avg_score = sum(scores) / len(scores) if scores else 0

        leaderboard.append({
            'user': user,
            'avg_score': round(avg_score, 1),
            'active_days': active_days
        })

    leaderboard.sort(key=lambda x: x['avg_score'], reverse=True)
    
    context = {
        'leaderboard': leaderboard
    }
    return render(request, 'admin_leaderboard.html', context)

@login_required
@admin_required
def admin_age(request):
    age_groups = {
        '15-20': User.objects.filter(
            is_superuser=False,
            userprofile__age__gte=15, userprofile__age__lte=20
        ).count(),
        '21-25': User.objects.filter(
            is_superuser=False,
            userprofile__age__gte=21, userprofile__age__lte=25
        ).count(),
        '26-30': User.objects.filter(
            is_superuser=False,
            userprofile__age__gte=26, userprofile__age__lte=30
        ).count(),
        '30+': User.objects.filter(
            is_superuser=False,
            userprofile__age__gt=30
        ).count(),
    }
    
    def get_top_habits_by_age(min_age, max_age):
        if max_age:
            users = User.objects.filter(
                is_superuser=False,
                userprofile__age__gte=min_age,
                userprofile__age__lte=max_age
            )
        else:
            users = User.objects.filter(
                is_superuser=False,
                userprofile__age__gt=min_age
            )

        top_habits = Habit.objects.filter(
            user__in=users
        ).values('habit_name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        return list(top_habits)
        
    context = {
        'count_15_20': age_groups['15-20'],
        'count_21_25': age_groups['21-25'],
        'count_26_30': age_groups['26-30'],
        'count_30_plus': age_groups['30+'],
        'habits_15_20': get_top_habits_by_age(15, 20),
        'habits_21_25': get_top_habits_by_age(21, 25),
        'habits_26_30': get_top_habits_by_age(26, 30),
        'habits_30_plus': get_top_habits_by_age(30, None),
    }
    return render(request, 'admin_age.html', context)
