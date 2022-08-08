from django.http import HttpResponseRedirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ListOrder, OrderItem
from rest_framework import status
from .serializers import OrderSerializer, OrderItemSerializer
from django.shortcuts import get_object_or_404
from .signals import add_list_order_to_profile
from knox.auth import TokenAuthentication
from rest_framework.views import APIView
from user.models import Profile
import json
import pandas as pd


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deleterOrderId(request, id_):
    orderItem = get_object_or_404(OrderItem, id=id_)
    # quantity = orderItem.quantity
    # count = request.data
    # count = count['count']
    # count += quantity
    OrderItem.objects.get(id=id_).delete()
    return HttpResponseRedirect(redirect_to='http://127.0.0.1:8000/order/myorders/')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orderId(request, id_):
    try:
        user = request.user
        order = ListOrder.objects.get(id=id_)

        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
        else:
            return Response({'detail': 'مجوز صادر نشد'}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'detail': 'سفارش موجود نیست'}, status=status.HTTP_404_NOT_FOUND)


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
        return self.get(request)
