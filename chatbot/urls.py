from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("conversations/", views.conversation_list, name="conversation_list"),
    path("conversations/<int:conversation_id>/", views.conversation_detail, name="conversation_detail"),
    path("conversations/new/", views.new_conversation, name="new_conversation"),
    path("conversations/<int:conversation_id>/delete/", views.delete_conversation, name="delete_conversation"),
]