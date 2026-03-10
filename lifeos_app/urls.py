from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('profile/', views.profile_view, name='profile_view'),
    
    path('goals/', views.goals_list, name='goals_list'),
    path('goals/delete/<int:goal_id>/', views.delete_goal, name='delete_goal'),
    path('goals/complete/<int:goal_id>/', views.complete_goal, name='complete_goal'),
    path('goals/edit/<int:goal_id>/', views.edit_goal, name='edit_goal'),

    path('habits/', views.habits_list, name='habits_list'),
    path('habits/delete/<int:habit_id>/', views.delete_habit, name='delete_habit'),
    path('habits/complete/<int:habit_id>/', views.complete_habit, name='complete_habit'),

    path('tasks/', views.tasks_list, name='tasks_list'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('tasks/complete/<int:task_id>/', views.complete_task, name='complete_task'),
    path('tasks/edit/<int:task_id>/', views.edit_task, name='edit_task'),

    path('reflections/', views.reflections_list, name='reflections_list'),
    path('reflections/delete/<int:reflection_id>/', views.delete_reflection, name='delete_reflection'),
    path('reflections/edit/<int:reflection_id>/', views.edit_reflection, name='edit_reflection'),
    
    path('reports/', views.reports_page, name='reports_page'),
    path('generate_report_csv/', views.generate_report_csv, name='generate_report'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-disable-user/<int:user_id>/', views.admin_disable_user, name='admin_disable_user'),
]
