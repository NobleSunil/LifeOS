import datetime
from .models import Task

def overdue_tasks_count(request):
    """
    Context processor to globally inject the count of overdue tasks
    for the authenticated user. Used primarily for the sidebar badge.
    """
    if request.user.is_authenticated:
        today = datetime.date.today()
        count = Task.objects.filter(
            user=request.user,
            status='Pending',
            due_date__lt=today
        ).count()
        return {'overdue_count': count}
    return {'overdue_count': 0}
