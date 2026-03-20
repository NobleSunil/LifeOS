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
    class Meta:
        model = Goal
        fields = ['title', 'description', 'status']

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['habit_name', 'goal', 'tracking_mode']
        widgets = {
            'tracking_mode': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # tracking_mode cannot be changed after creation
        if self.instance and self.instance.pk:
            self.fields['tracking_mode'].disabled = True

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'goal', 'habit', 'start_date', 'due_date', 'status', 'task_type']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'task_type': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # task_type cannot be changed after creation
        if self.instance and self.instance.pk:
            self.fields['task_type'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')

        if start_date and due_date and start_date > due_date:
            self.add_error('start_date', "Start date cannot be later than the due date.")
            
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
