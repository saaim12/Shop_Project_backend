from django.urls import path,include
from apps.core.views import home
urlpatterns = [
    path("api/v1/",include("api.v1.urls")),

]
