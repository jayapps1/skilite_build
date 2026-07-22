from django.urls import path

from .views import HomeView, AboutView, ContactView, ContactSuccessView


app_name = "core"


urlpatterns = [
    path(
        "",
        HomeView.as_view(),
        name="home",
    ),
    path(
        "about/",
        AboutView.as_view(),
        name="about",
    ),
    path(
        "contact/",
        ContactView.as_view(),
        name="contact",
    ),
    path(
        "contact/success/<str:enquiry_code>/",
        ContactSuccessView.as_view(),
        name="contact_success",
    ),
]