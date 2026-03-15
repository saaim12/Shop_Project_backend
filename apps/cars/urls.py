from django.urls import path

from apps.cars.views import CarDetailView, CarImageDetailView, CarImagesView, CarListCreateView


urlpatterns = [
    path("", CarListCreateView.as_view(), name="cars-list-create"),
    path("<str:car_id>", CarDetailView.as_view(), name="cars-detail"),
    path("<str:car_id>/images", CarImagesView.as_view(), name="cars-images"),
    path("images/<str:image_id>", CarImageDetailView.as_view(), name="cars-image-detail"),
]
