"""Custom permissions for the Shop Project backend."""

from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            User.Role.ADMIN,
            User.Role.MANAGER,
        )


class IsTechnician(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.TECHNICIAN,
        )


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True
        return getattr(obj, "user", None) == request.user
