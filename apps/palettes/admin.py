from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Palette, PaletteColor


class PaletteColorInline(admin.TabularInline):
    model = PaletteColor
    extra = 0

    fields = (
        "role",
        "hex_value",
    )


@admin.register(Palette)
class PaletteAdmin(admin.ModelAdmin):
    inlines = [
        PaletteColorInline,
    ]

    list_display = (
        "name",
        "owner",
        "source_type",
        "theme_mode",
        "visibility",
        "moderation_status",
        "is_published",
        "is_featured",
        "display_color_count",
        "created_at",
    )

    list_filter = (
        "source_type",
        "theme_mode",
        "visibility",
        "moderation_status",
        "is_published",
        "is_featured",
        "is_active",
        "business_category",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "description",
        "owner__username",
        "owner__email",
    )

    autocomplete_fields = (
        "owner",
        "business_category",
        "dominant_color_family",
        "source_palette",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "published_at",
    )

    fieldsets = (
        (
            "Palette information",
            {
                "fields": (
                    "owner",
                    "name",
                    "slug",
                    "description",
                ),
            },
        ),
        (
            "Classification",
            {
                "fields": (
                    "business_category",
                    "dominant_color_family",
                    "source_type",
                    "source_palette",
                    "theme_mode",
                ),
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "visibility",
                    "moderation_status",
                    "allow_export",
                    "is_published",
                    "is_featured",
                    "is_active",
                    "published_at",
                ),
            },
        ),
        (
            "Audit information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    ordering = (
        "-created_at",
    )

    list_select_related = (
        "owner",
        "business_category",
        "dominant_color_family",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.annotate(
            admin_color_count=Count(
                "colors",
                distinct=True,
            )
        )

    @admin.display(
        description="Colours",
        ordering="admin_color_count",
    )
    def display_color_count(self, obj):
        return obj.admin_color_count


@admin.register(PaletteColor)
class PaletteColorAdmin(admin.ModelAdmin):
    list_display = (
        "palette",
        "role",
        "display_colour",
        "created_at",
    )

    list_filter = (
        "role",
        "created_at",
    )

    search_fields = (
        "palette__name",
        "palette__slug",
        "hex_value",
    )

    autocomplete_fields = (
        "palette",
    )

    ordering = (
        "palette__name",
        "role",
    )

    @admin.display(
        description="Colour",
        ordering="hex_value",
    )
    def display_colour(self, obj):
        return format_html(
            (
                '<span style="'
                'display:inline-block;'
                'width:24px;'
                'height:24px;'
                'margin-right:8px;'
                'vertical-align:middle;'
                'border:1px solid #ced4da;'
                'border-radius:4px;'
                'background-color:{};'
                '"></span>{}'
            ),
            obj.hex_value,
            obj.hex_value,
        )
