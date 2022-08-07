from rest_framework import serializers
from .models import OrderItem, ListOrder
# from user.serializers import UserSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    orderItems = serializers.SerializerMethodField(read_only=True)
    # user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ListOrder
        fields = '__all__'

    def get_orderItems(self, obj):
        items = obj.orderitem_set.all()
        return OrderItemSerializer(items, many=True).data


