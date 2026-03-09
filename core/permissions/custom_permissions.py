from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to check if user is admin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow admins to edit and everyone to read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsSuperUser(permissions.BasePermission):
    """Allow access only to authenticated superusers."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class IsSelfOrSuperUser(permissions.BasePermission):
    """Allow access to own account, or any account for superusers."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        target_user_id = view.kwargs.get("user_id")
        if target_user_id is None:
            return True

        return request.user.is_superuser or str(request.user.id) == str(target_user_id)
