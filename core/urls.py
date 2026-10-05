from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    path("signin/", views.signin, name="signin"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            authentication_form=views.StyledAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("chats/", views.chat_list, name="chat_list"),
    path("chats/create/", views.create_group, name="create_group"),
    path("chats/<int:group_id>/", views.chat_detail, name="chat_detail"),
    path("chats/<int:group_id>/follow/", views.toggle_follow, name="toggle_follow"),
    path("profiles/<str:username>/", views.profile, name="profile"),
]
