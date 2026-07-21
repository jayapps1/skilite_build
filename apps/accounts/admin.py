from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserProfile, UserActivityLog


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0
    can_delete = False


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [
        UserProfileInline,
    ]

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    ordering = (
        "-date_joined",
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "display_name",
        "company_name",
        "preferred_language",
        "preferred_theme",
        "created_at",
    )

    list_filter = (
        "preferred_language",
        "preferred_theme",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "display_name",
        "company_name",
    )

    autocomplete_fields = (
        "user",
        "preferred_language",
    )


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "details",
        "ip_address",
        "created_at",
    )
    list_filter = (
        "action",
        "created_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "action",
        "details",
    )
