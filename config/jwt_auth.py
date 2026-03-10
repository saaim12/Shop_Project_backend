from datetime import datetime, timedelta, timezone

import jwt
from bson import ObjectId
from django.conf import settings
from rest_framework import authentication, exceptions

from apps.users.models import User


def create_access_token(user_id, role):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id, role):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.JWT_REFRESH_TOKEN_DAYS)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise exceptions.AuthenticationFailed("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise exceptions.AuthenticationFailed("Invalid token") from exc


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ", 1)[1].strip()
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise exceptions.AuthenticationFailed("Invalid access token")

        user_id = payload.get("sub")
        if not user_id:
            raise exceptions.AuthenticationFailed("Invalid token subject")

        try:
            user = User.objects.get(id=ObjectId(user_id), is_active=True)
        except Exception as exc:
            raise exceptions.AuthenticationFailed("User not found or inactive") from exc

        return user, token
