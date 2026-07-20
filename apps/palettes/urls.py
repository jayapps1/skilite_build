from django.urls import path
from django.views.generic import TemplateView


app_name = "palettes"


urlpatterns = [
    path(
        "editor/",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "Manual Color Editor",
                "page_message": (
                    "Create and preview a professional website "
                    "color palette."
                ),
            },
        ),
        name="editor",
    ),

    path(
        "my-palettes/",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "My Palettes",
                "page_message": (
                    "Your saved palettes will appear here."
                ),
            },
        ),
        name="my_palettes",
    ),

    path(
        "presets/",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "Preset Palettes",
                "page_message": (
                    "Browse professional palettes created "
                    "for different business categories."
                ),
            },
        ),
        name="presets",
    ),
]
