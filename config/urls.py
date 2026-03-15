from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from apps.core.views import home

handler404 = "config.exceptions.custom_404"

urlpatterns = [
    path("", home, name="health"),
    path("", include("apps.users.urls")),
    path("spare-parts/", include("apps.spare_parts.urls")),
    path("cars/", include("apps.cars.urls")),
    path("tyres/", include("apps.tyres.urls")),
    path("rims/", include("apps.rims.urls")),
    path("inventory/", include("apps.inventory.urls")),
]

if settings.DEBUG and not settings.USE_S3_STORAGE:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
