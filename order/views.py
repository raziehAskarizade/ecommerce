import datetime
import json

import pandas as pd
from django.shortcuts import get_object_or_404
from knox.auth import TokenAuthentication
from persiantools.jdatetime import JalaliDate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from user.models import Profile

from .models import ListOrder, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from .signals import add_list_order_to_profile


def change_date(order):
    year = order.date_submitted.year
    month = order.date_submitted.month
    day = order.date_submitted.day
    if year > 2020:
        iran_calender = JalaliDate(datetime.date(year, month, day))
        return str(iran_calender)
    return str(order.date_submitted)


class Order(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer
    serializer_item = OrderItemSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def get(self, request):
        self.objects = self.get_object()
        user = Profile.objects.get(user=self.objects)
        order_items = OrderItem.objects.filter(list_order=user.order.id)
        order_list = ListOrder.objects.get(id=int(str(order_items.first().list_order)))
        order_list_serializer = self.serializer_class(order_list)
        orders_serializer = self.serializer_item(order_items, many=True)
        orders_serializer = json.loads(json.dumps(orders_serializer.data))
        orders_serializer = pd.DataFrame(orders_serializer).to_dict()
        finally_response = {**orders_serializer, **dict(order_list_serializer.data)}
        return Response(finally_response)

    def post(self, request):
        self.objects = self.get_object()
        data = request.data
        orderItem = data['orderItems']
        if orderItem and len(orderItem) == 0:
            return Response({'detail': 'سفارشی نیست!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                order = ListOrder.objects.get(user=self.objects.phone)
            except:
                order = ListOrder.objects.create(
                    user=self.objects.phone,
                    total_price=data['total_price'],
                )
            changed_date = change_date(order)
            add_list_order_to_profile(order, order)
        for all_orders in orderItem:
            try:
                OrderItem.objects.filter(list_order=order, id_product=all_orders['id_product']).update(
                    quantity=all_orders['quantity'] + OrderItem.objects.get(list_order=order, id_product=all_orders[
                        'id_product']).quantity)
                if OrderItem.objects.get(list_order=order, id_product=all_orders['id_product']).quantity < 0:
                    return Response({"detail": "can't delete more!!"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                item = OrderItem.objects.create(
                    list_order=order,
                    id_product=all_orders['id_product'],
                    quantity=all_orders['quantity'],
                    price=all_orders['price']
                )
        order = ListOrder.objects.filter(user=self.objects.phone).update(date_submitted=changed_date)
        return self.get(request)


class OrderId(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer
    serializer_item = OrderItemSerializer

    def get(self, request, id_):
        try:
            user = request.user
            order = ListOrder.objects.get(id=id_)
            if user.is_staff or order.user == user.phone:
                serializer = self.serializer_class(order)
                order_items = OrderItem.objects.filter(list_order=order.id)
                orders_serializer = self.serializer_item(order_items, many=True)
                orders_serializer = json.loads(json.dumps(orders_serializer.data))
                orders_serializer = pd.DataFrame(orders_serializer).to_dict()
                finally_response = {**orders_serializer, **dict(serializer.data)}
                return Response(finally_response)
            else:
                return Response({'detail': 'مجوز صادر نشد'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'سفارش موجود نیست'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id_):
        orderItem = get_object_or_404(OrderItem, id_product=id_)
        OrderItem.objects.get(id_product=id_).delete()
        order = ListOrder.objects.get(user=request.user.phone)
        changed_date = change_date(order)
        ListOrder.objects.filter(user=request.user.phone).update(date_submitted=changed_date)
        data = {'orders': reverse('orders', request=request)}
        return Response(data)
