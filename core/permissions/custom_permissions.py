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
