import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "invoice_system.settings")
django.setup()

from django.conf import settings
from django.core.mail import send_mail

send_mail(
    "Test",
    "Hello from Jyaba Tech invoice system",
    settings.DEFAULT_FROM_EMAIL,      # onboarding@resend.dev
    ["prosujansubedi@gmail.com"],    # ← put a real email you can check
    fail_silently=False,
)