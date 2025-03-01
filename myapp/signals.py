from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from myapp.models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """When a new User is created, automatically create a matching Profile."""
    if created:
        Profile.objects.create(user=instance)
