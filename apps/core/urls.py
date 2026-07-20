from django.urls import path
from django.views.generic import TemplateView

from .views import HomeView


app_name = "core"


urlpatterns = [
    path(
        "",
        HomeView.as_view(),
        name="home",
    ),

    path(
        "about/",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "About Skilite Build",
                "page_message": (
                    "Learn more about the Skilite Build "
                    "website colour-system platform."
                ),
            },
        ),
        name="about",
    ),

    path(
        "contact/",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "Contact",
                "page_message": (
                    "The Skilite Build contact page "
                    "is being prepared."
                ),
            },
        ),
        name="contact",
    ),
]