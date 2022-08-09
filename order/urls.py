from . import views
from django.urls import path

urlpatterns = [
    path('', views.Order.as_view(), name='orders'),
    path('<int:id_>/', views.OrderId.as_view(), name='list_order'),
    path('<int:list_id>/<int:item_id>/', views.ListOrderChanges.as_view({'post': 'change_list_to_future'})),
    path('<int:list_id>/', views.ListOrderChanges.as_view({'put': 'change_list_to_old'})),
]
