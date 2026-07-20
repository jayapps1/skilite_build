from django.contrib import admin

from .models import (
    BusinessCategory,
    ColorFamily,
    DesignStyle,
    Language,
    Mood,
)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "native_name",
        "code",
        "is_active",
        "is_default",
    )

    list_filter = (
        "is_active",
        "is_default",
    )

    search_fields = (
        "name",
        "native_name",
        "code",
    )


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "display_order",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    ordering = (
        "display_order",
        "name",
    )


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(DesignStyle)
class DesignStyleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(ColorFamily)
class ColorFamilyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "sample_hex",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "slug",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }
