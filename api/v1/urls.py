from django.urls import path, include

urlpatterns = [
    path('users/', include('api.v1.views.user_views')),
    path('vehicles/', include('api.v1.views.vehicle_views')),
    path('services/', include('api.v1.views.service_views')),
    path('inventory/', include('api.v1.views.inventory_views')),
    path('orders/', include('api.v1.views.order_views')),
    path('appointments/', include('api.v1.views.appointment_views')),
    path('billing/', include('api.v1.views.billing_views')),
]
