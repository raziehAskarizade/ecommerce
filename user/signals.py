from django.db.models.signals import post_save, pre_save
from .models import Profile, User


def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, phone=instance.phone)


post_save.connect(receiver=user_created_receiver, sender=User)


def user_change_phone(sender, instance, *args, **kwargs):
    user = User.objects.filter(phone=instance.get('user'))
    if user.first() is not None and user.first() != instance.get('user'):
        raise Exception('same phone number')
    User.objects.filter(phone=instance.get('user')).update(phone=instance.get('phone'), name=instance.get('first_name'))


# pre_save.connect(receiver=user_change_phone, sender=Profile)
