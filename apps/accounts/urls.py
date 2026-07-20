from django.urls import path
from django.views.generic import TemplateView


app_name = "accounts"


urlpatterns = [
    path(
        "login/",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "Login",
                "page_message": (
                    "The login form will be connected after "
                    "the account models and forms are created."
                ),
            },
        ),
        name="login",
    ),

    path(
        "register/",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "Create Account",
                "page_message": (
                    "The registration form will be connected "
                    "after the custom user model is created."
                ),
            },
        ),
        name="register",
    ),

    path(
        "dashboard/",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "Dashboard",
                "page_message": (
                    "Your Skilite Build dashboard is under development."
                ),
            },
        ),
        name="dashboard",
    ),

    path(
        "profile/",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "My Profile",
                "page_message": (
                    "Profile management will be implemented soon."
                ),
            },
        ),
        name="profile",
    ),

    path(
        "settings/",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "Account Settings",
                "page_message": (
                    "Account settings will be implemented soon."
                ),
            },
        ),
        name="settings",
    ),
]
