from django.urls import path
from django.views.generic import TemplateView


app_name = "core"


urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="core/home.html",
        ),
        name="home",
    ),

    path(
        "about/",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "About Skilite Build",
                "page_message": (
                    "Learn more about the Skilite Build platform."
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
                "page_title": "Contact Us",
                "page_message": (
                    "The contact page will be implemented soon."
                ),
            },
        ),
        name="contact",
    ),
]
