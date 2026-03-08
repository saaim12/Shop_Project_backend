"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

API_V1 = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(API_V1 + "auth/", include("apps.accounts.urls")),
    path(API_V1 + "vehicles/", include("apps.vehicles.urls")),
    path(API_V1 + "customers/", include("apps.customers.urls")),
    path(API_V1 + "employees/", include("apps.employees.urls")),
    path(API_V1 + "services/", include("apps.services.urls")),
    path(API_V1 + "parts/", include("apps.parts.urls")),
    path(API_V1 + "suppliers/", include("apps.suppliers.urls")),
    path(API_V1 + "appointments/", include("apps.appointments.urls")),
    path(API_V1 + "orders/", include("apps.orders.urls")),
    path(API_V1 + "invoices/", include("apps.invoices.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
