from django.urls import path

from apps.spare_parts.views import (
    SparePartDetailView,
    SparePartImageDetailView,
    SparePartImagesView,
    SparePartListCreateView,
)


urlpatterns = [
    path("", SparePartListCreateView.as_view(), name="spare-parts-list-create"),
    path("<str:part_id>", SparePartDetailView.as_view(), name="spare-parts-detail"),
    path("<str:part_id>/images", SparePartImagesView.as_view(), name="spare-parts-images"),
    path("image/<str:image_id>", SparePartImageDetailView.as_view(), name="spare-parts-image-detail"),
]
