from django.urls import path
from django.views.generic import TemplateView


app_name = "transcription"


urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "Audio Transcription",
                "page_message": (
                    "Upload audio, generate a transcript, and "
                    "translate it into supported languages."
                ),
            },
        ),
        name="index",
    ),
]
