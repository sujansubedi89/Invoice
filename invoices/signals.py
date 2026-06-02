"""
Django Signals: auto-create UserProfile when a User is saved.
signals.py hooks into Django's ORM events.
"""
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Fires automatically after every User.save()."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
