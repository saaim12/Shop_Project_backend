from rest_framework.permissions import SAFE_METHODS, BasePermission


class CarPermission(BasePermission):
    message = "Only staff or admin can create cars"

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = getattr(request, "user", None)
        return bool(user and user.role in {"staff", "admin"})
