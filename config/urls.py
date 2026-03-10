from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from apps.core.views import home

handler404 = "config.exceptions.custom_404"

urlpatterns = [
    path("", home, name="health"),
    path("api/", include("apps.users.urls")),
    path("api/cars/", include("apps.cars.urls")),
    path("api/spare-parts/", include("apps.spare_parts.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
]

if settings.DEBUG and not settings.USE_S3_STORAGE:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
