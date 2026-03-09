from django.urls import path
from apps.users.views import (
    ChangePasswordView,
    UserCreateView,
    UserDeleteView,
    UserGetAllView,
    UserInfoView,
    UserLoginView,
    UserLogoutView,
    UserUpdateView,
    UserUpdatePhotoView,
)

urlpatterns = [
    path("create/", UserCreateView.as_view(), name="user-create"),
    #only super user can do this
    path("getall/", UserGetAllView.as_view(), name="user-getall"),
    path("info/", UserInfoView.as_view(), name="user-info"),
    path("update/", UserUpdateView.as_view(), name="user-update"),
    path("update-photo/", UserUpdatePhotoView.as_view(), name="user-update-photo"),
    path("change-password/", ChangePasswordView.as_view(), name="user-change-password"),
    path("login/", UserLoginView.as_view(), name="user-login"),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
    path("delete/<str:user_id>/", UserDeleteView.as_view(), name="user-delete"),

    # Backward-compatible aliases
    path("", UserCreateView.as_view(), name="user-create-legacy"),
    path("all/", UserGetAllView.as_view(), name="user-getall-legacy"),
]
