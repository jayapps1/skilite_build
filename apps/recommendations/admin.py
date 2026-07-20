from django.contrib import admin

from .models import (
    RecommendationRequest,
    RecommendationRequestAvoidedColor,
    RecommendationRule,
    RecommendationRuleAvoidedColor,
)


class RecommendationRuleAvoidedColorInline(
    admin.TabularInline
):
    model = RecommendationRuleAvoidedColor
    extra = 0

    autocomplete_fields = (
        "color_family",
    )


@admin.register(RecommendationRule)
class RecommendationRuleAdmin(admin.ModelAdmin):
    inlines = [
        RecommendationRuleAvoidedColorInline,
    ]

    list_display = (
        "name",
        "business_category",
        "mood",
        "design_style",
        "preferred_color_family",
        "theme_mode",
        "priority",
        "is_active",
        "template_palette",
    )

    list_filter = (
        "business_category",
        "mood",
        "design_style",
        "preferred_color_family",
        "theme_mode",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
        "business_category__name",
        "template_palette__name",
    )

    autocomplete_fields = (
        "business_category",
        "mood",
        "design_style",
        "preferred_color_family",
        "template_palette",
        "created_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-priority",
        "name",
    )

    fieldsets = (
        (
            "Rule information",
            {
                "fields": (
                    "name",
                    "description",
                    "created_by",
                ),
            },
        ),
        (
            "Matching criteria",
            {
                "fields": (
                    "business_category",
                    "mood",
                    "design_style",
                    "preferred_color_family",
                    "theme_mode",
                ),
            },
        ),
        (
            "Recommendation result",
            {
                "fields": (
                    "template_palette",
                    "priority",
                    "is_active",
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


class RecommendationRequestAvoidedColorInline(
    admin.TabularInline
):
    model = RecommendationRequestAvoidedColor
    extra = 0

    autocomplete_fields = (
        "color_family",
    )


@admin.register(RecommendationRequest)
class RecommendationRequestAdmin(admin.ModelAdmin):
    inlines = [
        RecommendationRequestAvoidedColorInline,
    ]

    list_display = (
        "id",
        "display_requester",
        "business_category",
        "mood",
        "design_style",
        "theme_mode",
        "selected_rule",
        "generated_palette",
        "created_at",
    )

    list_filter = (
        "business_category",
        "mood",
        "design_style",
        "theme_mode",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "session_key",
        "business_category__name",
        "selected_rule__name",
        "generated_palette__name",
    )

    autocomplete_fields = (
        "user",
        "business_category",
        "mood",
        "design_style",
        "preferred_color_family",
        "selected_rule",
        "generated_palette",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    @admin.display(description="Requester")
    def display_requester(self, obj):
        if obj.user_id:
            return obj.user.username

        return f"Guest: {obj.session_key[:12]}"


@admin.register(RecommendationRuleAvoidedColor)
class RecommendationRuleAvoidedColorAdmin(
    admin.ModelAdmin
):
    list_display = (
        "recommendation_rule",
        "color_family",
        "created_at",
    )

    list_filter = (
        "color_family",
        "created_at",
    )

    search_fields = (
        "recommendation_rule__name",
        "color_family__name",
    )

    autocomplete_fields = (
        "recommendation_rule",
        "color_family",
    )


@admin.register(RecommendationRequestAvoidedColor)
class RecommendationRequestAvoidedColorAdmin(
    admin.ModelAdmin
):
    list_display = (
        "recommendation_request",
        "color_family",
        "created_at",
    )

    list_filter = (
        "color_family",
        "created_at",
    )

    search_fields = (
        "recommendation_request__user__username",
        "recommendation_request__session_key",
        "color_family__name",
    )

    autocomplete_fields = (
        "recommendation_request",
        "color_family",
    )
