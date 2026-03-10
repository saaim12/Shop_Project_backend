from rest_framework.permissions import BasePermission


class InventoryPermission(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.role in {"staff", "admin"})
