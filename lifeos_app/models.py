# Import necessary modules from Django for database models and user authentication
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Model representing a user's profile information.
    This extends the built-in Django User model with additional personal details.
    Each user can have only one profile (one-to-one relationship).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the Django User model; if user is deleted, profile is also deleted
    full_name = models.CharField(max_length=200, blank=True)  # Optional field for the user's full name (up to 200 characters)
    bio = models.TextField(blank=True)  # Optional text field for user's biography or personal description
    age = models.IntegerField(blank=True, null=True)  # Optional age field for analytics

    def __str__(self):
        # Returns a string representation of the profile for display in admin interface
        return f"{self.user.username}'s Profile"

class Goal(models.Model):
    """
    Model representing a user's goals.
    Goals can be set by users to track their objectives, with status tracking.
    """
    STATUS_CHOICES = [
        ('Active', 'Active'),  # Goal is currently being worked on
        ('Completed', 'Completed'),  # Goal has been achieved
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Foreign key to User; goals are deleted if user is deleted
    title = models.CharField(max_length=200)  # Required title of the goal (up to 200 characters)
    description = models.TextField(blank=True, null=True)  # Optional detailed description of the goal
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')  # Status of the goal, defaults to 'Active'
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when goal is created
    completed_at = models.DateTimeField(blank=True, null=True)  # Optional timestamp when goal was completed

    def __str__(self):
        # Returns a string representation showing goal title and associated user
        return f"{self.title} - {self.user.username}"

    @property
    def total_tasks(self):
        return self.tasks.count()
        
    @property
    def completed_tasks(self):
        return self.tasks.filter(status='Completed').count()
        
    @property
    def progress_percentage(self):
        total = self.total_tasks
        return int((self.completed_tasks / total) * 100) if total > 0 else 0

class Habit(models.Model):
    """
    Model representing a user's habits.
    Habits are recurring activities that users want to track.
    """
    TRACKING_MODE_CHOICES = [
        ('manual_slider', 'Manual with Slider'),
        ('manual_checkbox', 'Manual with Checkbox'),
        ('task_driven', 'Task Driven'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Foreign key to User; habits are deleted if user is deleted
    habit_name = models.CharField(max_length=200)  # Name of the habit (up to 200 characters)
    goal = models.ForeignKey(Goal, on_delete=models.SET_NULL, null=True, blank=True, related_name='habits')
    tracking_mode = models.CharField(
        max_length=20,
        choices=TRACKING_MODE_CHOICES,
        default='manual_slider'
    )  # Cannot be changed after creation
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when habit is created

    def __str__(self):
        # Returns a string representation showing habit name and associated user
        return f"{self.habit_name} - {self.user.username}"

class HabitCompletion(models.Model):
    """
    Model tracking the completion of habits on specific dates.
    This allows users to mark whether they completed a habit each day.
    """
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)  # Foreign key to Habit; completion records are deleted if habit is deleted
    date = models.DateField()  # Date for which the habit completion is recorded
    completion_percentage = models.IntegerField(default=0)  # Percentage of habit completion for this date (0-100)

    class Meta:
        # Ensures only one completion record per habit per date
        unique_together = ('habit', 'date')

    def __str__(self):
        # Returns a string representation showing habit name, date, and completion percentage
        return f"{self.habit.habit_name} on {self.date} - {self.completion_percentage}%"

class Task(models.Model):
    """
    Model representing tasks that users need to complete.
    Tasks have due dates and can be marked as pending or completed.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),  # Task is not yet completed
        ('Completed', 'Completed'),  # Task has been finished
    ]
    TASK_TYPE_CHOICES = [
        ('simple', 'Simple'),
        ('trackable', 'Trackable'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Foreign key to User; tasks are deleted if user is deleted
    title = models.CharField(max_length=200)  # Required title of the task (up to 200 characters)
    description = models.TextField(blank=True, null=True)  # Optional detailed description of the task
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')  # Status of the task, defaults to 'Pending'
    task_type = models.CharField(
        max_length=10,
        choices=TASK_TYPE_CHOICES,
        default='simple'
    )  # Cannot be changed after creation
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )  # Only meaningful for trackable tasks
    goal = models.ForeignKey(Goal, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')  # Optional relation to Goal
    habit = models.ForeignKey(Habit, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    start_date = models.DateField(blank=True, null=True)  # Optional start date for the task
    due_date = models.DateField(blank=True, null=True)  # Optional due date for the task
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when task is created

    def __str__(self):
        # Returns the task title as its string representation
        return self.title

class Reflection(models.Model):
    """
    Model representing daily reflections by users.
    Users can write reflections for specific dates to track their thoughts and progress.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Foreign key to User; reflections are deleted if user is deleted
    date = models.DateField()  # Date of the reflection
    content = models.JSONField(default=dict)  # Content of the reflection stored as JSON
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when reflection is created

    class Meta:
        # Ensures only one reflection per user per date
        unique_together = ('user', 'date')

    def __str__(self):
        # Returns a string representation showing user and date of reflection
        return f"Reflection by {self.user.username} on {self.date}"
