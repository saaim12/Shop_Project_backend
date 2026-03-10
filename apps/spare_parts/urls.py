from django.urls import path

from apps.spare_parts.views import SparePartCreateDataView, SparePartDetailView, SparePartImagesView, SparePartListCreateView


urlpatterns = [
    path("", SparePartListCreateView.as_view(), name="spare-parts-list-create"),
    path("create-data/", SparePartCreateDataView.as_view(), name="spare-parts-create-data"),
    path("<str:part_id>/", SparePartDetailView.as_view(), name="spare-parts-detail"),
    path("<str:part_id>/images/", SparePartImagesView.as_view(), name="spare-parts-images"),
]
