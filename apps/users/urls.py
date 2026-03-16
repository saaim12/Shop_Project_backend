from django.urls import path

from apps.users.views import (
    RefreshTokenView,
    LogoutView,
    RegisterView,
    LoginView,
    ProfileView,
    ProfileDataView,
    UserByIdView,
    UsersListView,
    UserDeleteView,
)

urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/logout", LogoutView.as_view(), name="auth-logout"),
    path("auth/refresh", RefreshTokenView.as_view(), name="auth-refresh"),
    path("users", UsersListView.as_view(), name="users-list"),
    path("users/me", ProfileView.as_view(), name="profile-me"),
    # These endpoints are for admin use only, they allow getting user data by id and deleting users by id and updating user
    path("users/<str:user_id>", UserByIdView.as_view(), name="users-by-id"),
    path("profile_data/<str:user_id>", ProfileDataView.as_view(), name="profile-data"),
    path("users/delete/<str:user_id>", UserDeleteView.as_view(), name="user-delete"),
]