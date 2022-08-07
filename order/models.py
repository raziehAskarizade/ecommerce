from django.db import models
import os
import sys
from django.core.validators import MinValueValidator, MaxValueValidator

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]

sys.path.append(os.path.realpath('.'))
# from user.models import User


class ListOrder(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total_price = models.IntegerField()
    is_accept = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    # it means order item its not exits
    id_product = models.PositiveIntegerField(editable=True, default=0)
    list_order = models.ForeignKey(ListOrder, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1, blank=False, null=False)
    price = models.PositiveIntegerField(default=1, blank=False, null=False)

    def __str__(self):
        return str(self.id_product)
