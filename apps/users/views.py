from bson import ObjectId
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers import LoginSerializer, RegisterSerializer, UpdateProfileSerializer, UserSerializer
from apps.users.services import UserService
from apps.services.s3_service import UploadFailedError, UploadValidationError
from config.jwt_auth import create_access_token, create_refresh_token, decode_token
from config.response import error_response, extract_error_message, success_response


class RegisterView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        try:
            image_file = serializer.validated_data.get("image")
            user = UserService.create_user(serializer.validated_data, image_file=image_file)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadValidationError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadFailedError as exc:
            return error_response(str(exc), status.HTTP_502_BAD_GATEWAY)

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
            return error_response("Invalid email or password", status.HTTP_401_UNAUTHORIZED)

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


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = (request.data.get("refresh") or "").strip()
        if not token:
            return error_response("Invalid request data", status.HTTP_400_BAD_REQUEST)

        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return error_response("Invalid token", status.HTTP_401_UNAUTHORIZED)

        user = User.objects(id=ObjectId(payload["sub"]), is_active=True).first()
        if not user:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        access = create_access_token(user.id, user.role)
        return success_response({"access": access}, status.HTTP_200_OK, "Token refreshed successfully")


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Since we're using stateless JWT, logout is handled client-side by deleting tokens
        # This endpoint confirms the user's intent to logout and can be used for logging/analytics
        return success_response(
            {"message": "Logout successful. Please delete your access and refresh tokens."},
            status.HTTP_200_OK,
            "Logged out successfully",
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        return success_response(UserSerializer(request.user).data, message="Profile fetched successfully")

    def put(self, request):
        serializer = UpdateProfileSerializer(data=request.data, context={"user_id": str(request.user.id)})
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES.get("image") or request.FILES.get("profile_image")
        try:
            user = UserService.update_profile(request.user, serializer.validated_data, image_file)
        except UploadValidationError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)
        except UploadFailedError as exc:
            return error_response(str(exc), status.HTTP_502_BAD_GATEWAY)
        return success_response(UserSerializer(user).data, message="Profile updated successfully")


class UsersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "admin":
            return error_response("Only admin can list users", status.HTTP_403_FORBIDDEN)

        role_filter = (request.query_params.get("role") or "").strip().lower()
        if role_filter == "all":
            role_filter = ""

        if role_filter and role_filter not in {"customer", "staff", "admin"}:
            return error_response("Invalid role filter", status.HTTP_400_BAD_REQUEST)

        users_query = User.objects().order_by("-created_at")
        if role_filter:
            users_query = users_query.filter(role=role_filter)

        group_by_role = (request.query_params.get("group_by_role") or "").strip().lower() in {"1", "true", "yes"}
        if group_by_role:
            grouped = {"admin": [], "staff": [], "customer": []}
            for user in users_query:
                grouped.setdefault(user.role, []).append(UserSerializer(user).data)
            return success_response(grouped, message="Users fetched successfully")

        return success_response([UserSerializer(user).data for user in users_query], message="Users fetched successfully")


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if request.user.role != "admin":
            return error_response("Only admin can view users", status.HTTP_403_FORBIDDEN)
        try:
            target_user = User.objects.get(id=ObjectId(user_id))
        except Exception:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)
        return success_response(UserSerializer(target_user).data, message="User fetched successfully")

    def patch(self, request, user_id):
        if request.user.role != "admin":
            return error_response("Only admin can update users", status.HTTP_403_FORBIDDEN)
        try:
            target_user = User.objects.get(id=ObjectId(user_id))
        except Exception:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        data = request.data
        if "name" in data:
            target_user.name = data.get("name")
        if "phone" in data:
            target_user.phone = data.get("phone")
        if "role" in data:
            next_role = (data.get("role") or "").strip().lower()
            if next_role not in {"customer", "staff", "admin"}:
                return error_response("Invalid request data", status.HTTP_400_BAD_REQUEST)
            target_user.role = next_role

        target_user.save()
        return success_response(UserSerializer(target_user).data, message="User updated successfully")

    def delete(self, request, user_id):
        try:
            target_user = User.objects.get(id=ObjectId(user_id))
        except Exception:
            return error_response("User not found", status.HTTP_404_NOT_FOUND)

        try:
            UserService.delete_user(request.user, target_user)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_403_FORBIDDEN)

        return success_response(
            {"deleted": True},
            message="User deleted successfully"
        )
        