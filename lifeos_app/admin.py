from django.contrib import admin
from .models import Goal, Habit, HabitCompletion, Task, Reflection

admin.site.register(Goal)
admin.site.register(Habit)
admin.site.register(HabitCompletion)
admin.site.register(Task)
admin.site.register(Reflection)
