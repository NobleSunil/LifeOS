import csv
import datetime
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Count, Q
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
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    today = datetime.date.today()
    
    total_goals = Goal.objects.filter(user=user).count()
    completed_goals = Goal.objects.filter(user=user, status='Completed').count()
    
    total_tasks = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, status='Completed').count()
    
    total_habits = Habit.objects.filter(user=user).count()
    
    # Habits completed today
    completed_habits_today = HabitCompletion.objects.filter(
        habit__user=user, date=today, completed=True
    ).count()
    
    # Consistency Score (Using Today's habit completions and all-time tasks as the most sensible simple metric)
    denominator = total_habits + total_tasks
    numerator = completed_habits_today + completed_tasks
    consistency_score = round((numerator / denominator * 100) if denominator > 0 else 0)

    # For the Chart.js we need last 7 days consistency score
    last_7_days = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
    chart_labels = [d.strftime('%a') for d in last_7_days]
    chart_data = []
    
    for d in last_7_days:
        day_completed_habits = HabitCompletion.objects.filter(habit__user=user, date=d, completed=True).count()
        # For simplicity in historical graph, we use tasks completed on or before that day, 
        # but since Task doesn't have completion date, we'll just use overall completed tasks or a fixed number.
        # Let's approximate historical score by just mixing today's tasks and historical habits.
        day_numerator = day_completed_habits + completed_tasks
        day_score = round((day_numerator / denominator * 100) if denominator > 0 else 0)
        chart_data.append(day_score)

    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting_time = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting_time = "Good Afternoon"
    else:
        greeting_time = "Good Evening"

    try:
        display_name = user.userprofile.full_name.split()[0] if user.userprofile.full_name else user.username
    except UserProfile.DoesNotExist:
        display_name = user.username

    context = {
        'greeting_time': greeting_time,
        'display_name': display_name,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'total_habits': total_habits,
        'completed_habits_today': completed_habits_today,
        'consistency_score': consistency_score,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
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
@login_required
def habits_list(request):
    habits = Habit.objects.filter(user=request.user).order_by('-created_at')
    today = datetime.date.today()
    
    # Attach completion status for today to each habit
    for habit in habits:
        habit.is_completed_today = HabitCompletion.objects.filter(habit=habit, date=today, completed=True).exists()

    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            h = form.save(commit=False)
            h.user = request.user
            h.save()
            return redirect('habits_list')
    else:
        form = HabitForm()
    return render(request, 'habits.html', {'habits': habits, 'form': form})

@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    habit.delete()  # Cascade deletes HabitCompletions automatically
    return redirect('habits_list')

@login_required
def complete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    today = datetime.date.today()
    completion, created = HabitCompletion.objects.get_or_create(habit=habit, date=today)
    completion.completed = not completion.completed  # Toggle completion
    completion.save()
    return redirect('habits_list')

# ==================== TASKS ====================
@login_required
def tasks_list(request):
    tasks = Task.objects.filter(user=request.user).order_by('due_date')
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            t.save()
            return redirect('tasks_list')
    else:
        form = TaskForm()
    return render(request, 'tasks.html', {'tasks': tasks, 'form': form})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect('tasks_list')

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.status = 'Completed'
    task.save()
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
@login_required
def reflections_list(request):
    reflections = Reflection.objects.filter(user=request.user).order_by('-date')
    today = datetime.date.today()
    already_reflected = reflections.filter(date=today).exists()
    
    error_message = None
    if request.method == 'POST':
        if already_reflected:
            error_message = "You have already written a reflection for today."
            form = ReflectionForm()
        else:
            form = ReflectionForm(request.POST)
            if form.is_valid():
                r = form.save(commit=False)
                r.user = request.user
                r.date = today
                r.save()
                return redirect('reflections_list')
    else:
        form = ReflectionForm()
        
    return render(request, 'reflections.html', {
        'reflections': reflections, 
        'form': form, 
        'already_reflected': already_reflected,
        'error_message': error_message
    })

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
@login_required
def reports_page(request):
    error_message = None
    
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            user_joined_date = request.user.date_joined.date()
            
            # Validation 1: Date before registration
            if start_date < user_joined_date:
                error_message = "Reports cannot be generated for dates before your account was created."
            else:
                # Validation 2: Check for activity data in range
                completed_tasks = Task.objects.filter(user=request.user, status='Completed', created_at__date__gte=start_date, created_at__date__lte=end_date).exists()
                completed_habits = HabitCompletion.objects.filter(habit__user=request.user, completed=True, date__gte=start_date, date__lte=end_date).exists()
                completed_goals = Goal.objects.filter(user=request.user, status='Completed', completed_at__date__gte=start_date, completed_at__date__lte=end_date).exists()
                
                if not (completed_tasks or completed_habits or completed_goals):
                    error_message = "No activity data found for the selected date range."
                else:
                    return redirect(f'/generate_report_csv/?start={start_date_str}&end={end_date_str}')

    return render(request, 'reports.html', {'error_message': error_message})


@login_required
def generate_report_csv(request):
    user = request.user
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="lifeos_report_{user.username}_{start_date_str}_to_{end_date_str}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['LifeOS Activity Report'])
    writer.writerow(['User', user.username])
    writer.writerow(['Period', f'{start_date_str} to {end_date_str}'])
    writer.writerow([])
    writer.writerow(['Metric', 'Value'])
    
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    # Calculate metrics ONLY within the date range
    completed_goals = Goal.objects.filter(user=user, status='Completed', completed_at__date__gte=start_date, completed_at__date__lte=end_date).count()
    writer.writerow(['Goals Completed', completed_goals])
    
    completed_tasks = Task.objects.filter(user=user, status='Completed', created_at__date__gte=start_date, created_at__date__lte=end_date).count()
    writer.writerow(['Tasks Completed', completed_tasks])
    
    total_habit_completions = HabitCompletion.objects.filter(habit__user=user, completed=True, date__gte=start_date, date__lte=end_date).count()
    writer.writerow(['Habit Completions', total_habit_completions])
    
    return response

# ==================== ADMIN DASHBOARD ====================
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
        
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=7)
    
    # 1. Platform metrics (Excluding admins)
    base_users = User.objects.filter(is_superuser=False, is_staff=False)
    total_users = base_users.count()
    
    # Active Users = completed at least one task or habit in last 7 days
    active_users_last_7_days = base_users.filter(
        Q(task__status='Completed', task__created_at__date__gte=seven_days_ago) | 
        Q(habit__habitcompletion__completed=True, habit__habitcompletion__date__gte=seven_days_ago)
    ).distinct().count()
    
    total_goals = Goal.objects.filter(user__is_superuser=False, user__is_staff=False).count()
    total_habits = Habit.objects.filter(user__is_superuser=False, user__is_staff=False).count()
    total_tasks = Task.objects.filter(user__is_superuser=False, user__is_staff=False).count()
    
    # Habit Completion Rate
    total_habit_attempts = HabitCompletion.objects.filter(habit__user__is_superuser=False, habit__user__is_staff=False).count()
    completed_habit_records = HabitCompletion.objects.filter(completed=True, habit__user__is_superuser=False, habit__user__is_staff=False).count()
    habit_completion_rate = round((completed_habit_records / total_habit_attempts * 100) if total_habit_attempts > 0 else 0)
    
    # User Management and Leaderboards
    all_users = base_users.annotate(
        completed_tasks_count=Count('task', filter=Q(task__status='Completed'), distinct=True),
        completed_habits_count=Count('habit__habitcompletion', filter=Q(habit__habitcompletion__completed=True), distinct=True),
        active_days_count=Count('habit__habitcompletion__date', filter=Q(habit__habitcompletion__completed=True), distinct=True) # Approximate active days by distinct habit completion days
    )
    
    user_data_list = []
    
    for u in all_users:
        # Check active status in last 7 days for table
        is_active = Task.objects.filter(user=u, status='Completed', created_at__date__gte=seven_days_ago).exists() or \
                    HabitCompletion.objects.filter(habit__user=u, completed=True, date__gte=seven_days_ago).exists()
                    
        activity_score = u.completed_tasks_count + u.completed_habits_count
        
        # Consistency score formula equivalent
        total_user_habits = Habit.objects.filter(user=u).count()
        total_user_tasks = Task.objects.filter(user=u).count()
        total_possible = total_user_habits + total_user_tasks
        avg_consistency = round((activity_score / total_possible * 100) if total_possible > 0 else 0)
        
        user_data_list.append({
            'user': u,
            'is_active': is_active,
            'activity_score': activity_score,
            'avg_consistency': avg_consistency,
            'active_days_count': u.active_days_count,
            'date_joined': u.date_joined
        })
        
    top_active_users = sorted(user_data_list, key=lambda x: x['activity_score'], reverse=True)[:5]
    
    consistent_users = [u for u in user_data_list if u['active_days_count'] >= 5]
    consistency_leaderboard = sorted(consistent_users, key=lambda x: x['avg_consistency'], reverse=True)[:5]
    
    recent_users = base_users.order_by('-date_joined')[:5]
    
    # Platform Activity Chart (last 7 days completed tasks + habit completions)
    last_7_days = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
    chart_labels = [d.strftime('%a') for d in last_7_days]
    chart_data = []
    
    has_activity_data = False
    for d in last_7_days:
        day_tasks = Task.objects.filter(status='Completed', created_at__date=d, user__is_superuser=False, user__is_staff=False).count()
        day_habits = HabitCompletion.objects.filter(completed=True, date=d, habit__user__is_superuser=False, habit__user__is_staff=False).count()
        total_day_activity = day_tasks + day_habits
        chart_data.append(total_day_activity)
        if total_day_activity > 0:
            has_activity_data = True

    context = {
        'total_users': total_users,
        'active_users_last_7_days': active_users_last_7_days,
        'total_goals': total_goals,
        'total_habits': total_habits,
        'total_tasks': total_tasks,
        'habit_completion_rate': habit_completion_rate,
        'user_data_list': user_data_list,
        'top_active_users': top_active_users,
        'consistency_leaderboard': consistency_leaderboard,
        'recent_users': recent_users,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'has_activity_data': has_activity_data,
        'is_admin_dashboard': True,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def admin_disable_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('dashboard')
        
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)
        
        if target_user == request.user:
            return redirect('admin_dashboard') # Cannot disable self
            
        superusers_count = User.objects.filter(is_superuser=True, is_active=True).count()
        if target_user.is_superuser and target_user.is_active and superusers_count <= 1:
            return redirect('admin_dashboard') # Must keep at least one active admin
            
        # Toggle soft disable mapping to is_active
        target_user.is_active = not target_user.is_active
        target_user.save()
        
    return redirect('admin_dashboard')
