from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.users.models import User
from apps.users.serializers import UserSerializer
from apps.services.user_service import UserService
from apps.core.settings import SECRET_KEY_FOR_STAFF_USER, SECRET_KEY_FOR_ADMIN_USER


class UserListCreateView(APIView):

    def post(self, request):

        data = request.data.copy()
        image_file = request.FILES.get("image")

        user_type = data.get("user_type")
        key = data.get("key")
        is_superuser_flag = data.get("is_superuser")

        if isinstance(is_superuser_flag, str):
            is_superuser_flag = is_superuser_flag.lower() in {"true", "1", "yes"}
        else:
            is_superuser_flag = bool(is_superuser_flag)

        # -------- SUPERUSER CREATION --------
        if is_superuser_flag:

            if key != SECRET_KEY_FOR_ADMIN_USER:
                return Response(
                    {"error": "Invalid key for superuser creation"},
                    status=status.HTTP_403_FORBIDDEN
                )

            payload = data.copy()
            payload.pop("key", None)
            payload.pop("is_superuser", None)
            payload["user_type"] = "staff"

            serializer = UserSerializer(data=payload)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.create_superuser(
                    email=serializer.validated_data.get("email"),
                    password=serializer.validated_data.get("password"),
                    key=key,
                    first_name=serializer.validated_data.get("first_name"),
                    last_name=serializer.validated_data.get("last_name"),
                    phone=serializer.validated_data.get("phone"),
                    age=serializer.validated_data.get("age"),
                )
            except ValueError as exc:
                return Response(
                    {"error": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )

        # -------- STAFF CREATION --------
        if user_type == "staff":

            if key != SECRET_KEY_FOR_STAFF_USER:
                return Response(
                    {"error": "Invalid key for staff creation"},
                    status=status.HTTP_403_FORBIDDEN
                )

        data.pop("key", None)
        data.pop("is_superuser", None)

        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            user = UserService.create_user(serializer.validated_data, image_file)

            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllUsersView(APIView):

    def post(self, request):

        key = request.data.get("key")

        if key != SECRET_KEY_FOR_ADMIN_USER:
            return Response(
                {"error": "Only superuser can view all users"},
                status=status.HTTP_403_FORBIDDEN
            )

        users = User.objects.all()

        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)