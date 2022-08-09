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
from rest_framework import generics

from .models import ListOrder, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from .signals import add_list_order_to_profile
from .viewset_base import ViewSetBase


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

    # show all order list such as new, old and future
    def get(self, request):
        self.objects = self.get_object()
        order_list = ListOrder.objects.filter(user=self.objects.phone)
        order_list_serializer = self.serializer_class(order_list, many=True)
        order_list_serializer = json.loads(json.dumps(order_list_serializer.data))
        order_list_serializer = pd.DataFrame(order_list_serializer).to_dict()
        finally_response = {**order_list_serializer}
        return Response(finally_response)

    def post(self, request):
        self.objects = self.get_object()
        data = request.data
        orderItem = data['orderItems']
        if orderItem and len(orderItem) == 0:
            return Response({'detail': 'سفارشی نیست!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                order = ListOrder.objects.get(user=self.objects.phone, choices='new')
            except:
                order = ListOrder.objects.create(
                    user=self.objects.phone,
                    total_price=data['total_price'],
                    choices='new'
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
        order = ListOrder.objects.filter(user=self.objects.phone, choices='new').update(date_submitted=changed_date)
        data = {
            'list_order': reverse('list_order', args=[ListOrder.objects.get(user=self.objects.phone, choices='new').id],
                                  request=request)}
        return Response(data)


class OrderId(generics.UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer
    serializer_item = OrderItemSerializer

    # show each list order
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

    # delete fully an order item
    def delete(self, request, id_):
        orderItem = get_object_or_404(OrderItem, id_product=id_)
        OrderItem.objects.get(id_product=id_).delete()
        order = ListOrder.objects.get(user=request.user.phone)
        changed_date = change_date(order)
        ListOrder.objects.filter(user=request.user.phone).update(date_submitted=changed_date)
        data = {'orders': reverse('orders', request=request)}
        return Response(data)


class ListOrderChanges(ViewSetBase):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer
    serializer_item = OrderItemSerializer

    # call this method when decide to change is_received
    # we know that is validate in front-end by quantity that is not mines
    @staticmethod
    def change_list_to_future(request, list_id, item_id):
        try:
            check = ListOrder.objects.get(id=list_id)
            item_price = OrderItem.objects.get(list_order=check, id_product=item_id)
            future = ListOrder.objects.filter(user=request.user.phone, choices='future')
            price = item_price.quantity * item_price.price
        except:
            return Response({'detail': 'no such order item in list order to change'},
                            status=status.HTTP_400_BAD_REQUEST)
        if str(future) == '<QuerySet []>':
            future = ListOrder.objects.create(user=request.user.phone, total_price=0, choices='future')
        changed_date = change_date(future.first())
        future.update(total_price=price + ListOrder.objects.get(id=future.first().id).total_price,
                      date_submitted=changed_date)

        OrderItem.objects.filter(list_order=check, id_product=item_id).update(list_order=future.first().id)
        return Response({'detail': 'order item change to future check list'}, status=status.HTTP_200_OK)

    # def when list order start to sent to user
    @staticmethod
    def change_list_to_old(request, list_id):
        try:
            check = ListOrder.objects.get(id=list_id)
            item_price = OrderItem.objects.filter(list_order=check)
        except:
            return Response({'detail': 'no such order item in list order to change'},
                            status=status.HTTP_400_BAD_REQUEST)
        future = ListOrder.objects.filter(id=list_id).update(is_received=True, choices='old')
        OrderItem.objects.filter(list_order=check).update(list_order=future.first().id)
        data = {'list_order': reverse('list_order', args=[list_id], request=request)}
        return Response(data)
