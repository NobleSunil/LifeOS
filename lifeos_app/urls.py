from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('profile/', views.profile_view, name='profile_view'),
    
    path('goals/', views.goals_list, name='goals_list'),
    path('goals/delete/<int:goal_id>/', views.delete_goal, name='delete_goal'),
    path('goals/complete/<int:goal_id>/', views.complete_goal, name='complete_goal'),
    path('goals/edit/<int:goal_id>/', views.edit_goal, name='edit_goal'),

    path('habits/', views.habits_list, name='habits_list'),
    path('habits/delete/<int:habit_id>/', views.delete_habit, name='delete_habit'),
    path('habits/complete/<int:habit_id>/', views.complete_habit, name='complete_habit'),
    path('habits/edit/<int:habit_id>/', views.edit_habit, name='edit_habit'),
    path('habits/<int:habit_id>/log/', views.save_habit_log, name='save_habit_log'),

    path('tasks/', views.tasks_list, name='tasks_list'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('tasks/complete/<int:task_id>/', views.complete_task, name='complete_task'),
    path('tasks/edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/progress/', views.save_task_progress, name='save_task_progress'),

    path('reflections/', views.reflections_list, name='reflections_list'),
    path('reflections/delete/<int:reflection_id>/', views.delete_reflection, name='delete_reflection'),
    path('reflections/edit/<int:reflection_id>/', views.edit_reflection, name='edit_reflection'),
    
    path('reports/', views.reports_page, name='reports_page'),
    path('reports/summary/', views.report_summary_api, name='report_summary_api'),
    path('reports/generate/', views.generate_report, name='generate_report'),

    path('admin-panel/overview/', views.admin_dashboard_overview, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/activity/', views.admin_activity, name='admin_activity'),
    path('admin-panel/habits/', views.admin_habits, name='admin_habits'),
    path('admin-panel/leaderboard/', views.admin_leaderboard, name='admin_leaderboard'),
    path('admin-panel/age/', views.admin_age, name='admin_age'),
    
    path('admin-panel/users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
]
