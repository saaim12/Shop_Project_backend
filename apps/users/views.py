from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.users.models import User
from apps.users.serializers import UserSerializer
from apps.services.user_service import UserService
from apps.core.settings import SECRET_KEY_FOR_STAFF_USER

class UserListCreateView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
def post(self, request):

    data = request.data.copy()
    image_file = request.FILES.get("image")

    user_type = data.get("user_type", "customer")

    # staff creation requires secret key
    if user_type == "staff":
        key = data.get("key")

        if key != SECRET_KEY_FOR_STAFF_USER:
            return Response(
                {"error": "Invalid staff creation key"},
                status=status.HTTP_403_FORBIDDEN
            )

    serializer = UserSerializer(data=data)

    if serializer.is_valid():
        user = UserService.create_user(serializer.validated_data, image_file)

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        