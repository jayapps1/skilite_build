from django.urls import path
from django.views.generic import TemplateView

from .views import (
    PaletteCreateView,
    PaletteUpdateView,
)


app_name = "palettes"


urlpatterns = [
    path(
        "editor/",
        PaletteCreateView.as_view(),
        name="editor",
    ),
    path(
        "<slug:slug>/edit/",
        PaletteUpdateView.as_view(),
        name="edit",
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
                    "Browse professional preset colour systems."
                ),
            },
        ),
        name="presets",
    ),
]