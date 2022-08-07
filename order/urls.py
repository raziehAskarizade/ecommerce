from . import views
from django.urls import path

urlpatterns = [
    path('add/', views.addOrder, name='addOrder'),
    path('delete/<int:id_>/', views.deleterOrderId, name='deleteOrderId'),
    path('myorders/', views.getOrders, name='getOrders'),
    path('<int:id_>/', views.orderId, name='getOrderId'),
    # path('<int:user_id>/<int:month>/<int:day>/', views.getByTime, name='getByTime'),
]
