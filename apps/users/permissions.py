from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(getattr(request, "user", None) and request.user.role == "admin")


class IsStaffOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(getattr(request, "user", None) and request.user.role in {"staff", "admin"})


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(getattr(request, "user", None) and request.user.role == "customer")


class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.role == "admin" or str(obj.id) == str(request.user.id))
