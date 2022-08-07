from django.http import HttpResponseRedirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import ListOrder, OrderItem
from rest_framework import status
from .serializers import OrderSerializer
from django.shortcuts import get_object_or_404
from user.models import User


# @api_view(['GET'])
# @permission_classes([IsAdminUser])
# def getAllUser(request):
#     user = User.objects.all()
#     return Response(UserSerializer(user, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrder(request):
    user = request.user
    data = request.data
    orderItem = data['orderItems']
    if orderItem and len(orderItem) == 0:
        return Response({'detail': 'سفارشی نیست!'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            order = ListOrder.objects.get(user=user)
        except:
            order = ListOrder.objects.create(
                user=user,
                total_price=data['total_price'],
            )
    for all_orders in orderItem:
        try:
            # if OrderItem.objects.get(list_order=order, id_product=all_orders['id_product']).id_product != 0:
            OrderItem.objects.filter(list_order=order, id_product=all_orders['id_product']).update(
                quantity=all_orders['quantity'] + OrderItem.objects.get(list_order=order, id_product=all_orders[
                    'id_product']).quantity)
            if OrderItem.objects.get(list_order=order, id_product=all_orders['id_product']).quantity < 0:
                return Response({"detail": "can't delete more!!"}, status=status.HTTP_204_NO_CONTENT)
            # orderItem['count'] -= all_orders['quantity']
        except:
            item = OrderItem.objects.create(
                list_order=order,
                id_product=all_orders['id_product'],
                quantity=all_orders['quantity'],
                price=all_orders['price']
            )
            # all_orders['count'] -= item.quantity
            # all_orders.save()
    # else:
    #     return Response({'detail': 'موجودی کالا کافی نیست'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(OrderSerializer(order, many=False).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrders(request):
    user = request.user
    orderItem = get_object_or_404(OrderItem, get_object_or_404(ListOrder, user=user))
    # orderItem = [orderItem]  solve here
    # orderItem = [orderItem]  solve here`
    # OrderItem.objects.get(list_order=ListOrder.objects.get(user=user))
    orders_serializer = OrderSerializer(orderItem, many=True)
    return Response(orders_serializer.data)


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

# @api_view(['GET'])
# @permission_classes([IsAdminUser])
# def getByTime(request, user_id, month, day):
#     try:
#         user = User.objects.get(id=user_id)
#         order = ListOrder.objects.get(created__month=month, created__day=day)
#         if order.user == user:
#             serializer = OrderSerializer(order, many=False)
#             return Response(serializer.data)
#         else:
#             return Response({'detail': 'دسترسی ندارید'}, status=status.HTTP_400_BAD_REQUEST)
#     except:
#         return Response({'detail': 'سفارشی در این تاریخ ثبت نشده است'}, status=status.HTTP_404_NOT_FOUND)
