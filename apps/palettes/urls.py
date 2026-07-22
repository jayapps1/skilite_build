from django.urls import path

from .views import (
    ApplyPresetView,
    MyPaletteListView,
    PaletteCreateView,
    PaletteDeleteView,
    PaletteDetailView,
    PaletteDuplicateView,
    PaletteUpdateView,
    PresetPaletteListView,
    PalettePublishView,
    RecycleBinView,
    RestorePaletteView,
    PermanentDeletePaletteView,
)


app_name = "palettes"


urlpatterns = [
    path(
        "editor/",
        PaletteCreateView.as_view(),
        name="editor",
    ),
    path(
        "my-palettes/",
        MyPaletteListView.as_view(),
        name="my_palettes",
    ),
    path(
        "presets/",
        PresetPaletteListView.as_view(),
        name="presets",
    ),
    path(
        "recycle-bin/",
        RecycleBinView.as_view(),
        name="recycle_bin",
    ),
    path(
        "presets/<slug:slug>/apply/",
        ApplyPresetView.as_view(),
        name="apply_preset",
    ),
    path(
        "<slug:slug>/edit/",
        PaletteUpdateView.as_view(),
        name="edit",
    ),
    path(
        "<slug:slug>/duplicate/",
        PaletteDuplicateView.as_view(),
        name="duplicate",
    ),
    path(
        "<slug:slug>/delete/",
        PaletteDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<slug:slug>/restore/",
        RestorePaletteView.as_view(),
        name="restore",
    ),
    path(
        "<slug:slug>/permanent-delete/",
        PermanentDeletePaletteView.as_view(),
        name="permanent_delete",
    ),
    path(
        "<slug:slug>/publish/",
        PalettePublishView.as_view(),
        name="publish",
    ),
    path(
        "<slug:slug>/",
        PaletteDetailView.as_view(),
        name="detail",
    ),
]