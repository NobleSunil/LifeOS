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

    GOAL_TYPE_CHOICES = [
        ('task_based', 'Task Based'),
        ('habit_based', 'Habit Based'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField(
        blank=True,
        null=True
    )
    goal_type = models.CharField(
        max_length=20,
        choices=GOAL_TYPE_CHOICES,
        default='task_based'
    )
    target_days = models.IntegerField(
        null=True,
        blank=True,
        help_text='Only for Habit Based goals'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Active'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Goal type cannot change after creation
    # Enforced in form

    @property
    def progress_percentage(self):

        # TASK BASED GOAL
        if self.goal_type == 'task_based':
            tasks = self.tasks.all()
            if not tasks.exists():
                return 0
            total_possible = tasks.count() * 100
            actual_score = 0
            for task in tasks:
                if task.status == 'Completed':
                    actual_score += 100
                elif task.task_type == 'trackable':
                    actual_score += task.progress
            return round(
                (actual_score / total_possible) * 100
            )

        # HABIT BASED GOAL
        elif self.goal_type == 'habit_based':
            habits = self.linked_habits.all()
            if not habits.exists():
                return 0
            if not self.target_days:
                return 0

            from datetime import date
            today = date.today()
            habit_progresses = []

            for habit in habits:
                # count days this habit was logged
                # since goal was created
                if habit.habit_type == 'checkbox':
                    # checkbox: count days = 100%
                    days_done = HabitCompletion.objects.filter(
                        habit=habit,
                        date__gte=self.created_at.date(),
                        date__lte=today,
                        completion_percentage=100
                    ).count()
                else:
                    # slider: count days > 0%
                    days_done = HabitCompletion.objects.filter(
                        habit=habit,
                        date__gte=self.created_at.date(),
                        date__lte=today,
                        completion_percentage__gt=0
                    ).count()

                # cap at target days
                days_done = min(
                    days_done,
                    self.target_days
                )
                habit_progress = round(
                    (days_done / self.target_days) * 100
                )
                habit_progresses.append(habit_progress)

            # average across all linked habits
            return round(
                sum(habit_progresses) / len(habit_progresses)
            )

        return 0

    def __str__(self):
        return self.title

class Habit(models.Model):

    HABIT_TYPE_CHOICES = [
        ('checkbox', 'Checkbox'),
        ('slider', 'Slider'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    habit_name = models.CharField(max_length=200)
    habit_type = models.CharField(
        max_length=20,
        choices=HABIT_TYPE_CHOICES,
        default='checkbox'
    )
    goal = models.ForeignKey(
        'Goal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_habits'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # habit_type cannot change after creation
    # Enforced in form

    def __str__(self):
        return self.habit_name

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

    TASK_TYPE_CHOICES = [
        ('simple', 'Simple'),
        ('trackable', 'Trackable'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField(
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPE_CHOICES,
        default='simple'
    )
    progress = models.IntegerField(
        default=0
    )
    goal = models.ForeignKey(
        'Goal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    # REMOVED: habit FK completely removed
    start_date = models.DateField(
        null=True,
        blank=True
    )
    due_date = models.DateField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # task_type cannot change after creation
    # Enforced in form

    def __str__(self):
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
