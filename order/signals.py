from django.db.models.signals import post_save, pre_save
from .models import ListOrder
from user.models import Profile


def add_list_order_to_profile(sender, instance, *args, **kwargs):
    Profile.objects.filter(user__phone=instance.user).update(order=instance)


post_save.connect(receiver=add_list_order_to_profile, sender=ListOrder)
