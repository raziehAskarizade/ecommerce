from rest_framework import serializers
from .models import OrderItem, ListOrder


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.FloatField()

    class Meta:
        model = ListOrder
        fields = '__all__'
