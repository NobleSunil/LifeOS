import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lifeos_project.settings')
django.setup()

from django.contrib.auth.models import User
from lifeos_app.models import UserProfile

# Test User 1
if not User.objects.filter(username='testuser1').exists():
    u1 = User.objects.create_user(
        username='testuser1',
        email='test1@lifeos.com',
        password='testpass123'
    )
    UserProfile.objects.get_or_create(
        user=u1,
        defaults={
            'full_name': 'Test User One',
            'age': 22
        }
    )

# Test User 2 (for isolation testing)
if not User.objects.filter(username='testuser2').exists():
    u2 = User.objects.create_user(
        username='testuser2',
        email='test2@lifeos.com',
        password='testpass123'
    )
    UserProfile.objects.get_or_create(
        user=u2,
        defaults={
            'full_name': 'Test User Two',
            'age': 25
        }
    )

# Verify admin exists
admin = User.objects.get(username='noblesunil')
assert admin.is_superuser == True
print('Setup complete')
