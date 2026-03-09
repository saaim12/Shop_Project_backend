from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from core.pagination.custom_pagination import CustomPagination
from core.permissions.custom_permissions import IsSelfOrSuperUser, IsSuperUser
from apps.users.services import UserService
from apps.users.serializers import (
    ChangePasswordSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class UserCreateView(APIView):
    permission_classes = [AllowAny]

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

        if is_superuser_flag:
            if key != settings.SECRET_KEY_FOR_ADMIN_USER:
                return Response(
                    {"error": "Invalid key for superuser creation"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            payload = data.copy()
            payload.pop("key", None)
            payload.pop("is_superuser", None)
            payload["user_type"] = "staff"

            serializer = UserSerializer(data=payload)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = UserService.create_superuser(serializer.validated_data, key, image_file)
            except ValueError as exc:
                return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

        if user_type == "staff" and key != settings.SECRET_KEY_FOR_STAFF_USER:
            return Response(
                {"error": "Invalid key for staff creation"},
                status=status.HTTP_403_FORBIDDEN,
            )

        data.pop("key", None)
        data.pop("is_superuser", None)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = UserService.create_user(serializer.validated_data, image_file)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserGetAllView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        is_active_raw = request.query_params.get("is_active")
        parsed_is_active = None
        if is_active_raw is not None:
            normalized = is_active_raw.strip().lower()
            if normalized in {"true", "1", "yes"}:
                parsed_is_active = True
            elif normalized in {"false", "0", "no"}:
                parsed_is_active = False
            else:
                raise ValidationError({"is_active": "Use true/false"})

        users = UserService.list_users(
            {
                "email": request.query_params.get("email"),
                "user_type": request.query_params.get("user_type"),
                "is_active": parsed_is_active,
            }
        )

        paginator = CustomPagination()
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""

        if not email or not password:
            return Response(
                {"error": "email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"error": "User account is inactive"},
                status=status.HTTP_403_FORBIDDEN,
            )

        login(request, user)

        user_data = UserSerializer(user).data

        return Response(
            {
                "message": "Login successful",
                "photo": user_data.get("image"),
                "user": user_data,
            },
            status=status.HTTP_200_OK,
        )


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = UserService.get_user_info(request.user.id)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        user_data = UserSerializer(user).data
        return Response(
            {
                "photo": user_data.get("image"),
                "user": user_data,
            },
            status=status.HTTP_200_OK,
        )


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsSelfOrSuperUser]

    def delete(self, request, user_id):
        hard_delete = (request.query_params.get("hard") or "").strip().lower() in {
            "true",
            "1",
            "yes",
        }
        if hard_delete and not request.user.is_superuser:
            return Response(
                {"error": "Only superuser can hard-delete users"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            if hard_delete:
                UserService.delete_user(user_id)
            else:
                UserService.soft_delete_user(user_id)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        if str(request.user.id) == str(user_id):
            logout(request)

        message = "User hard-deleted successfully" if hard_delete else "User deactivated successfully"
        return Response({"message": message}, status=status.HTTP_200_OK)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES.get("image")

        try:
            user = UserService.update_user_profile(request.user.id, serializer.validated_data, image_file)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        user_data = UserSerializer(user).data
        return Response(
            {
                "message": "Profile updated successfully",
                "photo": user_data.get("image"),
                "user": user_data,
            },
            status=status.HTTP_200_OK,
        )


class UserUpdatePhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        image_file = request.FILES.get("image")
        if not image_file:
            return Response(
                {"error": "image file is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = UserService.update_user_profile(request.user.id, {}, image_file)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        user_data = UserSerializer(user).data
        return Response(
            {
                "message": "Photo updated successfully",
                "photo": user_data.get("image"),
                "user": user_data,
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        try:
            UserService.change_password(request.user, old_password, new_password)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Keep sessions secure after password change.
        logout(request)
        return Response(
            {"message": "Password changed successfully. Please login again."},
            status=status.HTTP_200_OK,
        )


__all__ = [
    "UserCreateView",
    "UserGetAllView",
    "UserLoginView",
    "UserLogoutView",
    "UserInfoView",
    "UserDeleteView",
    "UserUpdateView",
    "UserUpdatePhotoView",
    "ChangePasswordView",
]

