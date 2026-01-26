from .models import User, UserProfile
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save,sender=User)
def createProfile(sender, instance, created, **kwargs):
    if created:
        profile= UserProfile.objects.create(user=instance)