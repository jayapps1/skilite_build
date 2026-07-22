from django.contrib import admin
from django.utils import timezone

from .models import (
    BusinessCategory,
    ColorFamily,
    DesignStyle,
    Language,
    Mood,
    ContactEnquiry,
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


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "enquiry_code",
        "full_name",
        "email",
        "enquiry_type",
        "subject",
        "status",
        "is_read",
        "assigned_to",
        "created_at",
    )

    list_filter = (
        "status",
        "enquiry_type",
        "is_read",
        "created_at",
    )

    search_fields = (
        "enquiry_code",
        "full_name",
        "email",
        "phone",
        "subject",
        "message",
    )

    readonly_fields = (
        "enquiry_code",
        "user",
        "full_name",
        "email",
        "phone",
        "enquiry_type",
        "subject",
        "message",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Enquiry Info", {
            "fields": (
                "enquiry_code",
                "user",
                "full_name",
                "email",
                "phone",
                "enquiry_type",
                "subject",
                "message",
                "created_at",
                "updated_at",
            )
        }),
        ("Moderation / Response", {
            "fields": (
                "status",
                "is_read",
                "assigned_to",
                "responded_at",
                "admin_notes",
            )
        }),
    )

    actions = [
        "mark_as_read_action",
        "mark_in_progress_action",
        "mark_resolved_action",
        "mark_spam_action",
    ]

    def mark_as_read_action(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Selected enquiries have been marked as read.")
    mark_as_read_action.short_description = "Mark selected as read"

    def mark_in_progress_action(self, request, queryset):
        queryset.update(status="IN_PROGRESS")
        self.message_user(request, "Selected enquiries have been marked as In Progress.")
    mark_in_progress_action.short_description = "Mark selected as in progress"

    def mark_resolved_action(self, request, queryset):
        for enquiry in queryset:
            enquiry.mark_resolved()
        self.message_user(request, "Selected enquiries have been marked as resolved.")
    mark_resolved_action.short_description = "Mark selected as resolved"

    def mark_spam_action(self, request, queryset):
        queryset.update(status="SPAM")
        self.message_user(request, "Selected enquiries have been marked as spam.")
    mark_spam_action.short_description = "Mark selected as spam"
