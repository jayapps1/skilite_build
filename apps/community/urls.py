from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    path("", views.CommunityGalleryView.as_view(), name="gallery"),
    path("copy/<slug:slug>/", views.CopyCommunityPaletteView.as_view(), name="copy"),
    path("like/<slug:slug>/", views.PaletteLikeToggleView.as_view(), name="like"),
    path("report/<slug:slug>/", views.PaletteReportView.as_view(), name="report"),
    path("track-view/<slug:slug>/", views.TrackViewCountView.as_view(), name="track_view"),
    path("palettes/<slug:slug>/", views.CommunityPaletteDetailView.as_view(), name="palette_detail"),
    path("palettes/<slug:slug>/export/<str:export_format>/", views.ExportPaletteView.as_view(), name="export_palette"),
]
