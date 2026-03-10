from django.urls import path

from apps.users.views import LoginView, LogoutView, ProfileView, RefreshTokenView, RegisterView, UserDetailView, UsersListView


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
    path("users/me/", ProfileView.as_view(), name="users-me"),
    path("users/profile/", ProfileView.as_view(), name="users-profile"),
    path("users/getall", UsersListView.as_view(), name="users-list"),
    path("users/<str:user_id>/", UserDetailView.as_view(), name="users-detail"),
    path("users/deleting/<str:user_id>/", UserDetailView.as_view(), name="users-delete"),
]
