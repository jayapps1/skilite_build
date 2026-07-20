from django.urls import path
from django.views.generic import TemplateView


app_name = "recommendations"


urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="base/coming_soon.html",
            extra_context={
                "page_title": "Business Recommendations",
                "page_message": (
                    "Select a business category, mood, style, "
                    "preferred color, and theme to generate "
                    "professional palette recommendations."
                ),
            },
        ),
        name="index",
    ),
]
