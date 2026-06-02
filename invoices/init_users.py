from django.contrib.auth.models import User
from .models import UserProfile

def create_demo_users():

    users = [
        ("admin", "admin123", "admin"),
        ("manager", "manager123", "manager"),
        ("employee", "employee123", "employee"),
    ]

    for username, password, role in users:

        if not User.objects.filter(username=username).exists():

            user = User.objects.create_user(
                username=username,
                password=password
            )

            UserProfile.objects.create(
                user=user,
                role=role
            )