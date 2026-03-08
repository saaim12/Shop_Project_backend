from django.urls import path
from api.v1.views.user_views import UserListCreateView, AllUsersView

urlpatterns = [
    path("", UserListCreateView.as_view(), name="user-list-create"),
    path("all/", AllUsersView.as_view(), name="all-users"),
]