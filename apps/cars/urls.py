from django.urls import path

from apps.cars.views import CarCreateView, CarDetailView, CarImagesView, CarListView


urlpatterns = [
    path("get-all/", CarListView.as_view(), name="cars-list"),
    path("create/", CarCreateView.as_view(), name="cars-create"),
    path("<str:car_id>/", CarDetailView.as_view(), name="cars-detail"),
    path("<str:car_id>/images/", CarImagesView.as_view(), name="cars-images"),
]
