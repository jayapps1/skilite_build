from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # Django administration
    path("admin/", admin.site.urls),

    # Language translation switching
    path("i18n/", include("django.conf.urls.i18n")),

    # Public/core pages
    path("", include("apps.core.urls")),

    # User accounts and authentication
    path("accounts/", include("apps.accounts.urls")),

    # Palette editor and saved palettes
    path("palettes/", include("apps.palettes.urls")),

    # Business palette recommendations
    path(
        "recommendations/",
        include("apps.recommendations.urls"),
    ),

    # Public palette community
    path(
        "community/",
        include("apps.community.urls"),
    ),

    # Optional transcription module
    path(
        "transcription/",
        include("apps.transcription.urls"),
    ),
]


# Serve uploaded media during local development.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
