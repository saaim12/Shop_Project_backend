from django.urls import path

from apps.tyres.views import TyreDetailView, TyreImageDetailView, TyreImagesView, TyreListCreateView


urlpatterns = [
    path("", TyreListCreateView.as_view(), name="tyres-list-create"),
    path("<str:tyre_id>", TyreDetailView.as_view(), name="tyres-detail"),
    path("<str:tyre_id>/images", TyreImagesView.as_view(), name="tyres-images"),
    path("images/<str:image_id>", TyreImageDetailView.as_view(), name="tyres-image-detail"),
]
