from rest_framework.permissions import BasePermission


def role_of(user):
    return (getattr(user, "role", "") or "").upper()


class IsAdmin(BasePermission):

    def has_permission(self, request, view):

        return bool(request.user and role_of(request.user) == "ADMIN")


class IsStaffOrAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and role_of(request.user) in {"STAFF", "ADMIN"})


class IsSelfOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):

        if role_of(request.user) == "ADMIN":
            return True

        return str(obj.id) == str(request.user.id)


class IsSelfOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return str(obj.id) == str(request.user.id)