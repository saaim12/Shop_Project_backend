from bson import ObjectId
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.services.s3_service import S3Service, UploadFailedError, UploadValidationError
from apps.users.models import User
from apps.users.permissions import role_of
from apps.users.serializers import LoginSerializer, RegisterSerializer, UpdateProfileSerializer, UserSerializer
from apps.users.services import UserService
from config.jwt_auth import blacklist_token, create_access_token, create_refresh_token, decode_token
from config.response import error_response, extract_error_message, success_response


def _get_uploaded_image_file(request):
    image_file = request.FILES.get("image")
    if image_file:
        return image_file

    candidate = request.data.get("image")
    if candidate is not None and hasattr(candidate, "read"):
        return candidate

    return None


def _replace_user_image(user, image_file):
    old_image = (getattr(user, "image", "") or "").strip()

    try:
        new_image_url = S3Service().upload_image(image_file, folder=settings.S3_USERS_FOLDER)
    except (UploadValidationError, UploadFailedError) as exc:
        raise ValueError(str(exc)) from exc

    try:
        user.image = new_image_url
        user.save()
    except Exception as exc:
        try:
            S3Service().delete_image(new_image_url)
        except Exception:
            pass
        raise ValueError("Failed to update profile image") from exc

    if old_image:
        try:
            S3Service().delete_image(old_image)
        except Exception:
            pass


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data.copy()
        image_file = _get_uploaded_image_file(request)
        if "image" in payload:
            payload.pop("image")

        serializer = RegisterSerializer(data=payload)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        validated_payload = dict(serializer.validated_data)
        uploaded_image_url = ""
        if image_file:
            try:
                uploaded_image_url = S3Service().upload_image(image_file, folder=settings.S3_USERS_FOLDER)
                validated_payload["image"] = uploaded_image_url
            except (UploadValidationError, UploadFailedError) as exc:
                return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        actor = request.user if getattr(request.user, "is_authenticated", False) else None
        try:
            user = UserService.create_user(validated_payload, actor_user=actor)
        except ValueError as exc:
            if uploaded_image_url:
                try:
                    S3Service().delete_image(uploaded_image_url)
                except Exception:
                    pass
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except Exception:
            if uploaded_image_url:
                try:
                    S3Service().delete_image(uploaded_image_url)
                except Exception:
                    pass
            return error_response("Failed to create user", status.HTTP_400_BAD_REQUEST)

        return success_response(UserSerializer(user).data, status.HTTP_201_CREATED, "User created successfully")


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"].strip().lower()
        password = serializer.validated_data["password"]

        user = User.objects(email=email, is_active=True).first()
        if not user or not user.check_password(password):
            return error_response("Invalid credentials", status.HTTP_401_UNAUTHORIZED)

        access = create_access_token(user.id, user.role)
        refresh = create_refresh_token(user.id, user.role)

        return success_response(
            {
                "access": access,
                "refresh": refresh,
                "user": UserSerializer(user).data,
            },
            status.HTTP_200_OK,
            "Login successful",
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ", 1)[1].strip()
            blacklist_token(access_token)

        refresh_token = (request.data.get("refresh") or "").strip()
        if refresh_token:
            blacklist_token(refresh_token)

        return success_response({"message": "Logout successful"}, status.HTTP_200_OK, "Logged out successfully")


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = (request.data.get("refresh") or "").strip()
        if not refresh_token:
            return error_response("refresh token is required", status.HTTP_400_BAD_REQUEST)

        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            return error_response("Invalid token type", status.HTTP_401_UNAUTHORIZED)

        user = User.objects(id=ObjectId(payload["sub"]), is_active=True).first()
        if not user:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        blacklist_token(refresh_token, payload=payload)

        access = create_access_token(user.id, user.role)
        refresh = create_refresh_token(user.id, user.role)
        return success_response({"access": access, "refresh": refresh}, status.HTTP_200_OK, "Token refreshed successfully")


class UsersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if role_of(request.user) != "ADMIN":
            return error_response("Only admin can list users", status.HTTP_403_FORBIDDEN)

        users = User.objects().order_by("-created_at")
        return success_response([UserSerializer(user).data for user in users], message="Users fetched successfully")


class UserByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if role_of(request.user) != "ADMIN":
            return error_response("Only admin can view users", status.HTTP_403_FORBIDDEN)

        try:
            target_user = User.objects.get(id=ObjectId(user_id))
        except Exception:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        return success_response(UserSerializer(target_user).data, message="User fetched successfully")

    def patch(self, request, user_id):
        if user_id == "me":
            target_user = request.user
        else:
            try:
                target_user = User.objects.get(id=ObjectId(user_id))
            except Exception:
                return error_response("User not found", status.HTTP_404_NOT_FOUND)

        requester_is_admin = role_of(request.user) == "ADMIN"
        requester_is_self = str(request.user.id) == str(target_user.id)

        if not requester_is_admin and not requester_is_self:
            return error_response("Forbidden", status.HTTP_403_FORBIDDEN)

        if requester_is_admin and not requester_is_self:
            target_role = (getattr(target_user, "role", "") or "").upper()
            if target_role == "CUSTOMER":
                return error_response("Admin cannot update customer accounts", status.HTTP_403_FORBIDDEN)

        payload = request.data.copy()
        image_file = _get_uploaded_image_file(request)
        if "image" in payload:
            payload.pop("image")

        if "role" in payload:
            if not requester_is_admin:
                return error_response("Only admin can update role", status.HTTP_403_FORBIDDEN)
            role = (payload.get("role") or "").upper()
            if role not in {"CUSTOMER", "STAFF", "ADMIN"}:
                return error_response("Invalid role", status.HTTP_400_BAD_REQUEST)
            payload["role"] = role

        serializer = UpdateProfileSerializer(data=payload, context={"user_id": str(target_user.id)})
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        merged_payload = dict(serializer.validated_data)
        if "role" in payload:
            merged_payload["role"] = payload["role"]

        try:
            updated_user = UserService.update_user(target_user, merged_payload)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        if image_file:
            try:
                _replace_user_image(updated_user, image_file)
            except ValueError as exc:
                return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        return success_response(UserSerializer(updated_user).data, message="User updated successfully")


class ProfileDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if role_of(request.user) != "ADMIN" and str(request.user.id) != str(user_id):
            return error_response("Forbidden", status.HTTP_403_FORBIDDEN)

        try:
            target_user = User.objects.get(id=ObjectId(user_id))
        except Exception:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        return success_response(UserSerializer(target_user).data, message="Profile data fetched successfully")


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(UserSerializer(request.user).data, message="Profile fetched successfully")

    def patch(self, request):
        target_user = request.user

        payload = request.data.copy()
        image_file = _get_uploaded_image_file(request)
        if "image" in payload:
            payload.pop("image")

        if "role" in payload:
            return error_response("Only admin can update role", status.HTTP_403_FORBIDDEN)

        serializer = UpdateProfileSerializer(data=payload, context={"user_id": str(target_user.id)})
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        try:
            updated_user = UserService.update_user(target_user, serializer.validated_data)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        if image_file:
            try:
                _replace_user_image(updated_user, image_file)
            except ValueError as exc:
                return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        return success_response(UserSerializer(updated_user).data, message="Profile updated successfully")


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        if user_id == "me":
            target_user = request.user
        else:
            try:
                target_user = User.objects.get(id=ObjectId(user_id))
            except Exception:
                return error_response("User not found", status.HTTP_404_NOT_FOUND)

        try:
            UserService.delete_user(request.user, target_user)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_403_FORBIDDEN)

        return success_response({"deleted": True}, message="User deleted successfully")
