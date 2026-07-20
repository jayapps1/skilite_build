from django.urls import path
from django.views.generic import TemplateView


app_name = "community"


urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "Community Gallery",
                "page_message": (
                    "Discover, like, copy, and export palettes "
                    "published by the Skilite Build community."
                ),
            },
        ),
        name="gallery",
    ),
]
