from django.contrib import admin

from .models import (
    PaletteCopy,
    PaletteExport,
    PaletteLike,
    PaletteReport,
    PaletteView,
)


@admin.register(PaletteLike)
class PaletteLikeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "palette",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "palette__name",
    )

    autocomplete_fields = (
        "user",
        "palette",
    )

    ordering = (
        "-created_at",
    )


@admin.register(PaletteCopy)
class PaletteCopyAdmin(admin.ModelAdmin):
    list_display = (
        "copied_by",
        "source_palette",
        "destination_palette",
        "copy_type",
        "created_at",
    )

    list_filter = (
        "copy_type",
        "created_at",
    )

    search_fields = (
        "copied_by__username",
        "copied_by__email",
        "source_palette__name",
        "destination_palette__name",
    )

    autocomplete_fields = (
        "copied_by",
        "source_palette",
        "destination_palette",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


@admin.register(PaletteReport)
class PaletteReportAdmin(admin.ModelAdmin):
    list_display = (
        "palette",
        "reported_by",
        "reason",
        "status",
        "reviewed_by",
        "created_at",
        "reviewed_at",
    )

    list_filter = (
        "status",
        "created_at",
        "reviewed_at",
    )

    search_fields = (
        "palette__name",
        "reported_by__username",
        "reported_by__email",
        "reason",
        "description",
        "admin_note",
    )

    autocomplete_fields = (
        "palette",
        "reported_by",
        "reviewed_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "reviewed_at",
    )

    ordering = (
        "-created_at",
    )


@admin.register(PaletteExport)
class PaletteExportAdmin(admin.ModelAdmin):
    list_display = (
        "palette",
        "user",
        "export_format",
        "display_export_actor",
        "created_at",
    )

    list_filter = (
        "export_format",
        "created_at",
    )

    search_fields = (
        "palette__name",
        "user__username",
        "user__email",
        "session_key",
    )

    autocomplete_fields = (
        "palette",
        "user",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    @admin.display(description="Actor")
    def display_export_actor(self, obj):
        if obj.user_id:
            return obj.user.username

        if obj.session_key:
            return f"Guest: {obj.session_key[:12]}"

        return "Unknown"


@admin.register(PaletteView)
class PaletteViewAdmin(admin.ModelAdmin):
    list_display = (
        "palette",
        "user",
        "display_viewer",
        "viewed_at",
    )

    list_filter = (
        "viewed_at",
    )

    search_fields = (
        "palette__name",
        "user__username",
        "user__email",
        "session_key",
        "ip_hash",
    )

    autocomplete_fields = (
        "palette",
        "user",
    )

    readonly_fields = (
        "viewed_at",
    )

    ordering = (
        "-viewed_at",
    )

    @admin.display(description="Viewer")
    def display_viewer(self, obj):
        if obj.user_id:
            return obj.user.username

        if obj.session_key:
            return f"Guest: {obj.session_key[:12]}"

        return "Unknown"
