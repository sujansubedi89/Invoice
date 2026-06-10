from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from invoices.models import UserProfile
class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        users=[
                      ("admin", "admin123", "admin"),
            ("manager", "manager123", "manager"),
            ("employee", "employee123", "employee"),
            ("guest","guest123","guest"),
        ]
        for username,password,role in users:
            if not User.objects.filter(username=username).exists():
                user=User.objects.create_user(username=username,password=password)
                UserProfile.objects.create(user=user,
                                           role=role)
                self.stdout.write(self.style.SUCCESS(f"Created user: {username} with role: {role}"))
            else:
                self.stdout.write(self.style.WARNING(f"User {username} already exists. Skipping."))