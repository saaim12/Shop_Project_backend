from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination.custom_pagination import CustomPagination
from core.permissions.custom_permissions import IsSelfOrSuperUser, IsSuperUser
from apps.users.services import UserService
from apps.users.serializers import (
    ChangePasswordSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


def _error_response(message, status_code, field_errors=None):
    payload = {
        "success": False,
        "message": message,
    }
    if field_errors:
        payload["field_errors"] = field_errors
    return Response(payload, status=status_code)


def _success_response(message, status_code=status.HTTP_200_OK, data=None):
    payload = {
        "success": True,
        "message": message,
    }
    if data is not None:
        payload["data"] = data
    return Response(payload, status=status_code)


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
                return _error_response(
                    "Invalid admin key",
                    status.HTTP_403_FORBIDDEN,
                    {"key": ["Invalid key for superuser creation"]},
                )

            payload = data.copy()
            payload.pop("key", None)
            payload.pop("is_superuser", None)
            payload["user_type"] = "staff"

            serializer = UserSerializer(data=payload)
            if not serializer.is_valid():
                return _error_response(
                    "Validation failed",
                    status.HTTP_400_BAD_REQUEST,
                    serializer.errors,
                )

            try:
                user = UserService.create_superuser(serializer.validated_data, key, image_file)
            except ValueError as exc:
                return _error_response(str(exc), status.HTTP_400_BAD_REQUEST)
            except DjangoValidationError as exc:
                return _error_response(
                    "Validation failed",
                    status.HTTP_400_BAD_REQUEST,
                    getattr(exc, "message_dict", {"non_field_errors": exc.messages}),
                )

            return _success_response(
                "User created successfully",
                status.HTTP_201_CREATED,
                UserSerializer(user).data,
            )

        if user_type == "staff" and key != settings.SECRET_KEY_FOR_STAFF_USER:
            return _error_response(
                "Invalid staff key",
                status.HTTP_403_FORBIDDEN,
                {"key": ["Invalid key for staff creation"]},
            )

        data.pop("key", None)
        data.pop("is_superuser", None)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            try:
                user = UserService.create_user(serializer.validated_data, image_file)
            except ValueError as exc:
                return _error_response(str(exc), status.HTTP_400_BAD_REQUEST)
            except DjangoValidationError as exc:
                return _error_response(
                    "Validation failed",
                    status.HTTP_400_BAD_REQUEST,
                    getattr(exc, "message_dict", {"non_field_errors": exc.messages}),
                )
            return _success_response(
                "User created successfully",
                status.HTTP_201_CREATED,
                UserSerializer(user).data,
            )

        return _error_response(
            "Validation failed",
            status.HTTP_400_BAD_REQUEST,
            serializer.errors,
        )


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
                return _error_response(
                    "Validation failed",
                    status.HTTP_400_BAD_REQUEST,
                    {"is_active": ["Use true/false"]},
                )

        users = UserService.list_users(
            {
                "email": request.query_params.get("email"),
                "user_type": request.query_params.get("user_type"),
                "is_active": parsed_is_active,
            }
        )

        raw_user_type = (request.query_params.get("user_type") or "").strip()
        if raw_user_type and raw_user_type not in {"customer", "staff"}:
            return _error_response(
                "Validation failed",
                status.HTTP_400_BAD_REQUEST,
                {"user_type": ["Use 'customer' or 'staff'"]},
            )

        paginator = CustomPagination()
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(paginated_users, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        return _success_response("Users fetched successfully", data=paginated_response.data)


class UserGetByCategoryView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request, category):
        normalized_category = (category or "").strip().lower()
        category_aliases = {
            "customer": "customer",
            "customers": "customer",
            "staff": "staff",
        }

        user_type = category_aliases.get(normalized_category)
        if not user_type:
            return _error_response(
                "Validation failed",
                status.HTTP_400_BAD_REQUEST,
                {"category": ["Use 'customers' or 'staff'"]},
            )

        users = UserService.list_users({"user_type": user_type})

        paginator = CustomPagination()
        paginated_users = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(paginated_users, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        return _success_response("Users fetched successfully", data=paginated_response.data)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""

        if not email or not password:
            field_errors = {}
            if not email:
                field_errors["email"] = ["Email is required"]
            if not password:
                field_errors["password"] = ["Password is required"]
            return _error_response(
                "Validation failed",
                status.HTTP_400_BAD_REQUEST,
                field_errors,
            )

        user = authenticate(request, username=email, password=password)
        if not user:
            return _error_response("Invalid credentials", status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return _error_response("User account is inactive", status.HTTP_403_FORBIDDEN)

        login(request, user)

        user_data = UserSerializer(user).data

        return _success_response(
            "Login successful",
            data={
                "photo": user_data.get("image"),
                "user": user_data,
            },
        )


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return _success_response("Logout successful")


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = UserService.get_user_info(request.user.id)
        except ValueError as exc:
            return _error_response(str(exc), status.HTTP_404_NOT_FOUND)

        user_data = UserSerializer(user).data
        return _success_response(
            "User info fetched successfully",
            data={
                "photo": user_data.get("image"),
                "user": user_data,
            },
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
            return _error_response("Only superuser can hard-delete users", status.HTTP_403_FORBIDDEN)

        try:
            if hard_delete:
                UserService.delete_user(user_id)
            else:
                UserService.soft_delete_user(user_id)
        except ValueError as exc:
            return _error_response(str(exc), status.HTTP_404_NOT_FOUND)

        if str(request.user.id) == str(user_id):
            logout(request)

        message = "User hard-deleted successfully" if hard_delete else "User deactivated successfully"
        return _success_response(message)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response(
                "Validation failed",
                status.HTTP_400_BAD_REQUEST,
                serializer.errors,
            )

        image_file = request.FILES.get("image")

        try:
            user = UserService.update_user_profile(request.user.id, serializer.validated_data, image_file)
        except ValueError as exc:
            return _error_response(str(exc), status.HTTP_404_NOT_FOUND)
        except DjangoValidationError as exc:
            return _error_response(
                "Validation failed",
                status.HTTP_400_BAD_REQUEST,
                getattr(exc, "message_dict", {"non_field_errors": exc.messages}),
            )
        except Exception as exc:
            return _error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        user_data = UserSerializer(user).data
        return _success_response(
            "Profile updated successfully",
            data={
                "photo": user_data.get("image"),
                "user": user_data,
            },
        )


class UserUpdatePhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        image_file = request.FILES.get("image")
        if not image_file:
            return _error_response(
                "Validation failed",
                status.HTTP_400_BAD_REQUEST,
                {"image": ["Image file is required"]},
            )

        try:
            user = UserService.update_user_profile(request.user.id, {}, image_file)
        except ValueError as exc:
            return _error_response(str(exc), status.HTTP_404_NOT_FOUND)
        except DjangoValidationError as exc:
            return _error_response(
                "Validation failed",
                status.HTTP_400_BAD_REQUEST,
                getattr(exc, "message_dict", {"non_field_errors": exc.messages}),
            )
        except Exception as exc:
            return _error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        user_data = UserSerializer(user).data
        return _success_response(
            "Photo updated successfully",
            data={
                "photo": user_data.get("image"),
                "user": user_data,
            },
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response(
                "Validation failed",
                status.HTTP_400_BAD_REQUEST,
                serializer.errors,
            )

        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        try:
            UserService.change_password(request.user, old_password, new_password)
        except ValueError as exc:
            return _error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        # Keep sessions secure after password change.
        logout(request)
        return _success_response("Password changed successfully. Please login again.")


__all__ = [
    "UserCreateView",
    "UserGetAllView",
    "UserGetByCategoryView",
    "UserLoginView",
    "UserLogoutView",
    "UserInfoView",
    "UserDeleteView",
    "UserUpdateView",
    "UserUpdatePhotoView",
    "ChangePasswordView",
]

