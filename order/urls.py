from . import views
from django.urls import path

urlpatterns = [
    path('', views.Order.as_view()),
    path('delete/<int:id_>/', views.deleterOrderId, name='deleteOrderId'),
    path('<int:id_>/', views.orderId, name='getOrderId'),
]
