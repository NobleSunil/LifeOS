from django import forms
from django.contrib.auth.models import User
from .models import Goal, Habit, Task, Reflection, UserProfile

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['full_name', 'bio', 'age']

    def __init__(self, *args, **kwargs):
        self.user_obj = kwargs.pop('user_obj', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.user_obj:
            self.fields['email'].initial = self.user_obj.email

    def save(self, commit=True):
        profile = super(UserProfileForm, self).save(commit=False)
        if self.user_obj:
            self.user_obj.email = self.cleaned_data['email']
            if commit:
                self.user_obj.save()
        if commit:
            profile.save()
        return profile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    age = forms.IntegerField(required=False, min_value=0, label="Age (Optional)")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data

class GoalForm(forms.ModelForm):

    GOAL_TYPE_CHOICES = [
        ('task_based', 'Task Based'),
        ('habit_based', 'Habit Based'),
    ]

    goal_type = forms.ChoiceField(
        choices=GOAL_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='task_based',
        required=True
    )

    target_days = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'e.g. 30',
                'min': '1'
            }
        )
    )

    class Meta:
        model = Goal
        fields = [
            'title',
            'description',
            'goal_type',
            'target_days'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lock goal_type after creation
        if self.instance and self.instance.pk:
            self.fields['goal_type'].disabled = True
            self.fields['target_days'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        goal_type = cleaned_data.get('goal_type')
        target_days = cleaned_data.get('target_days')

        # Habit Based goals MUST have target_days
        if goal_type == 'habit_based' and not target_days:
            self.add_error(
                'target_days',
                'Please set a target number of days '
                'for your habit based goal.'
            )

        # Task Based goals should NOT have target_days
        if goal_type == 'task_based':
            cleaned_data['target_days'] = None

        return cleaned_data

class HabitForm(forms.ModelForm):

    HABIT_TYPE_CHOICES = [
        ('checkbox', 'Checkbox — Did I do it or not?'),
        ('slider', 'Slider — How much did I do?'),
    ]

    habit_type = forms.ChoiceField(
        choices=HABIT_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='checkbox',
        required=True
    )

    class Meta:
        model = Habit
        fields = [
            'habit_name',
            'habit_type',
            'goal'
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Lock habit_type after creation
        if self.instance and self.instance.pk:
            self.fields['habit_type'].disabled = True

        # Only show Habit Based Goals
        # in the goal dropdown
        if self.user:
            self.fields['goal'].queryset = Goal.objects.filter(
                user=self.user,
                goal_type='habit_based',
                status='Active'
            )
        self.fields['goal'].required = False
        self.fields['goal'].empty_label = '── No Goal'

class TaskForm(forms.ModelForm):

    TASK_TYPE_CHOICES = [
        ('simple', 'Simple — Just mark complete when done'),
        ('trackable', 'Trackable — Track progress % along the way'),
    ]

    task_type = forms.ChoiceField(
        choices=TASK_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='simple',
        required=True
    )

    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'task_type',
            'goal',
            'start_date',
            'due_date',
            'status'
        ]
        # REMOVED: habit field completely removed

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Lock task_type after creation
        if self.instance and self.instance.pk:
            self.fields['task_type'].disabled = True

        # Only show Task Based Goals
        # in the goal dropdown
        if self.user:
            self.fields['goal'].queryset = Goal.objects.filter(
                user=self.user,
                goal_type='task_based',
                status='Active'
            )
        self.fields['goal'].required = False
        self.fields['goal'].empty_label = '── No Goal'

        # Date pickers
        self.fields['start_date'].widget = forms.DateInput(
            attrs={'type': 'date'}
        )
        self.fields['due_date'].widget = forms.DateInput(
            attrs={'type': 'date'}
        )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')

        if start_date and due_date:
            if start_date > due_date:
                self.add_error(
                    'start_date',
                    'Start date cannot be after due date.'
                )
        return cleaned_data


class ReflectionForm(forms.ModelForm):
    wins = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=True, label="Wins")
    challenges = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Challenges")
    tomorrow = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Tomorrow")

    class Meta:
        model = Reflection
        fields = []

    def __init__(self, *args, **kwargs):
        super(ReflectionForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            data = self.instance.content
            if isinstance(data, dict):
                self.fields['wins'].initial = data.get('wins', '')
                self.fields['challenges'].initial = data.get('challenges', '')
                self.fields['tomorrow'].initial = data.get('tomorrow', '')
            elif isinstance(data, str):
                import json
                try:
                    parsed = json.loads(data)
                    self.fields['wins'].initial = parsed.get('wins', '')
                    self.fields['challenges'].initial = parsed.get('challenges', '')
                    self.fields['tomorrow'].initial = parsed.get('tomorrow', '')
                except json.JSONDecodeError:
                    self.fields['wins'].initial = data

    def save(self, commit=True):
        reflection = super(ReflectionForm, self).save(commit=False)
        reflection.content = {
            'wins': self.cleaned_data.get('wins', ''),
            'challenges': self.cleaned_data.get('challenges', ''),
            'tomorrow': self.cleaned_data.get('tomorrow', '')
        }
        if commit:
            reflection.save()
        return reflection
