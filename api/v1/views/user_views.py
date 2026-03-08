from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.users.serializers import UserSerializer
from rest_framework.viewsets import ModelViewSet
from apps.users.models import User

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = router.urls
