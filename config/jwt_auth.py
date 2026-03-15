from datetime import datetime, timedelta, timezone
import hashlib
from uuid import uuid4

import jwt
from bson import ObjectId
from django.conf import settings
from mongoengine.errors import NotUniqueError
from rest_framework import authentication, exceptions

from apps.users.models import BlacklistedToken, User


def create_access_token(user_id, role):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "jti": str(uuid4()),
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
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.JWT_REFRESH_TOKEN_DAYS)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def _token_hash(token):
    return hashlib.sha256((token or "").encode("utf-8")).hexdigest()


def is_token_blacklisted(token):
    if not token:
        return False
    return BlacklistedToken.objects(token_hash=_token_hash(token)).first() is not None


def blacklist_token(token, payload=None):
    if not token:
        return

    internal_payload = payload
    if internal_payload is None:
        try:
            internal_payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": False},
            )
        except jwt.InvalidTokenError:
            return

    exp = internal_payload.get("exp")
    if not exp:
        return

    token_type = internal_payload.get("type") if internal_payload.get("type") in {"access", "refresh"} else "refresh"

    try:
        BlacklistedToken(
            token_hash=_token_hash(token),
            token_type=token_type,
            expires_at=datetime.fromtimestamp(int(exp), tz=timezone.utc),
        ).save()
    except NotUniqueError:
        return


def decode_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise exceptions.AuthenticationFailed("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise exceptions.AuthenticationFailed("Invalid token") from exc

    if is_token_blacklisted(token):
        raise exceptions.AuthenticationFailed("Token revoked")

    return payload


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
