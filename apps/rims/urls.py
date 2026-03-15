from django.urls import path

from apps.rims.views import RimDetailView, RimImageDetailView, RimImagesView, RimListCreateView


urlpatterns = [
    path("", RimListCreateView.as_view(), name="rims-list-create"),
    path("<str:rim_id>", RimDetailView.as_view(), name="rims-detail"),
    path("<str:rim_id>/images", RimImagesView.as_view(), name="rims-images"),
    path("images/<str:image_id>", RimImageDetailView.as_view(), name="rims-image-detail"),
]
