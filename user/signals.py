from django.db.models.signals import post_save, pre_save
from .models import Profile, User


def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, phone=instance.phone)


post_save.connect(receiver=user_created_receiver, sender=User)
