from django import forms
from django.contrib.auth.models import User
from .models import Goal, Habit, Task, Reflection, UserProfile

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['full_name', 'bio']

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
        fields = ['habit_name']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'start_date', 'due_date', 'status']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')

        if start_date and due_date and start_date > due_date:
            self.add_error('start_date', "Start date cannot be later than the due date.")
            
        return cleaned_data

class ReflectionForm(forms.ModelForm):
    class Meta:
        model = Reflection
        fields = ['content']
