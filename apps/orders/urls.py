from django.urls import path

from apps.orders.views import OrderDetailView, OrderListCreateView


urlpatterns = [
    path("", OrderListCreateView.as_view(), name="orders-list-create"),
    path("<str:order_id>/", OrderDetailView.as_view(), name="orders-detail"),
]
