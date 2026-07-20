from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.choices import PaletteSource, ThemeMode
from apps.core.models import TimeStampedModel


class RecommendationRuleQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def for_business(self, business_category):
        return self.active().filter(
            business_category=business_category,
        )

    def ordered_for_matching(self):
        return self.active().order_by(
            "-priority",
            "name",
        )


class RecommendationRule(TimeStampedModel):
    """
    Rule used to select a recommendation-template palette.
    """

    name = models.CharField(
        max_length=150,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    business_category = models.ForeignKey(
        "core.BusinessCategory",
        on_delete=models.PROTECT,
        related_name="recommendation_rules",
    )

    mood = models.ForeignKey(
        "core.Mood",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="recommendation_rules",
    )

    design_style = models.ForeignKey(
        "core.DesignStyle",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="recommendation_rules",
    )

    preferred_color_family = models.ForeignKey(
        "core.ColorFamily",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="preferred_recommendation_rules",
    )

    template_palette = models.ForeignKey(
        "palettes.Palette",
        on_delete=models.PROTECT,
        related_name="recommendation_rules",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_recommendation_rules",
    )

    theme_mode = models.CharField(
        max_length=10,
        choices=ThemeMode.choices,
        default=ThemeMode.LIGHT,
    )

    priority = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    avoided_color_families = models.ManyToManyField(
        "core.ColorFamily",
        through="RecommendationRuleAvoidedColor",
        blank=True,
        related_name="avoided_by_recommendation_rules",
    )

    objects = RecommendationRuleQuerySet.as_manager()

    class Meta:
        db_table = "recommendation_rules"
        ordering = ["-priority", "name"]

        indexes = [
            models.Index(
                fields=[
                    "business_category",
                    "mood",
                    "design_style",
                    "theme_mode",
                ],
                name="rec_rule_match_idx",
            ),
            models.Index(
                fields=["is_active", "-priority"],
                name="rec_rule_active_idx",
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        errors = {}

        if self.template_palette_id:
            template = self.template_palette

            if (
                template.source_type
                != PaletteSource.RECOMMENDATION_TEMPLATE
            ):
                errors["template_palette"] = (
                    "The selected palette must have the source type "
                    "'Recommendation Template'."
                )

            if template.theme_mode != self.theme_mode:
                errors["theme_mode"] = (
                    "The recommendation rule theme must match "
                    "the template palette theme."
                )

            if (
                template.business_category_id
                and template.business_category_id
                != self.business_category_id
            ):
                errors["business_category"] = (
                    "The rule business category must match "
                    "the template palette business category."
                )

            if not template.is_active:
                errors["template_palette"] = (
                    "An inactive palette cannot be used as a template."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class RecommendationRuleAvoidedColor(TimeStampedModel):
    """
    Color family that should be excluded by a recommendation rule.
    """

    recommendation_rule = models.ForeignKey(
        RecommendationRule,
        on_delete=models.CASCADE,
        related_name="avoided_color_records",
    )

    color_family = models.ForeignKey(
        "core.ColorFamily",
        on_delete=models.PROTECT,
        related_name="recommendation_rule_avoidances",
    )

    class Meta:
        db_table = "recommendation_rule_avoided_colors"
        ordering = ["color_family"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "recommendation_rule",
                    "color_family",
                ],
                name="unique_rule_avoided_color",
            ),
        ]

    def __str__(self):
        return (
            f"{self.recommendation_rule.name} avoids "
            f"{self.color_family.name}"
        )

    def clean(self):
        super().clean()

        if (
            self.recommendation_rule_id
            and self.color_family_id
            and self.recommendation_rule.preferred_color_family_id
            == self.color_family_id
        ):
            raise ValidationError(
                {
                    "color_family": (
                        "The preferred color family cannot also "
                        "be an avoided color family."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class RecommendationRequestQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

    def for_session(self, session_key):
        return self.filter(session_key=session_key)

    def recent(self):
        return self.order_by("-created_at")


class RecommendationRequest(TimeStampedModel):
    """
    Recommendation request submitted by a registered user or guest.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommendation_requests",
    )

    business_category = models.ForeignKey(
        "core.BusinessCategory",
        on_delete=models.PROTECT,
        related_name="recommendation_requests",
    )

    mood = models.ForeignKey(
        "core.Mood",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommendation_requests",
    )

    design_style = models.ForeignKey(
        "core.DesignStyle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommendation_requests",
    )

    preferred_color_family = models.ForeignKey(
        "core.ColorFamily",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="preferred_recommendation_requests",
    )

    selected_rule = models.ForeignKey(
        RecommendationRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommendation_requests",
    )

    generated_palette = models.OneToOneField(
        "palettes.Palette",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recommendation_request",
    )

    theme_mode = models.CharField(
        max_length=10,
        choices=ThemeMode.choices,
        default=ThemeMode.LIGHT,
    )

    session_key = models.CharField(
        max_length=255,
        blank=True,
    )

    avoided_color_families = models.ManyToManyField(
        "core.ColorFamily",
        through="RecommendationRequestAvoidedColor",
        blank=True,
        related_name="avoided_by_recommendation_requests",
    )

    objects = RecommendationRequestQuerySet.as_manager()

    class Meta:
        db_table = "recommendation_requests"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "-created_at"],
                name="rec_request_user_idx",
            ),
            models.Index(
                fields=[
                    "business_category",
                    "theme_mode",
                    "-created_at",
                ],
                name="rec_request_business_idx",
            ),
            models.Index(
                fields=["session_key", "-created_at"],
                name="rec_request_session_idx",
            ),
        ]

    def __str__(self):
        if self.user_id:
            actor = self.user.username
        elif self.session_key:
            actor = f"Guest {self.session_key[:8]}"
        else:
            actor = "Guest"

        return f"{actor} - {self.business_category.name}"

    def clean(self):
        super().clean()

        errors = {}

        self.session_key = self.session_key.strip()

        if not self.user_id and not self.session_key:
            errors["session_key"] = (
                "A guest recommendation request requires "
                "a browser session key."
            )

        if self.selected_rule_id:
            if (
                self.selected_rule.business_category_id
                != self.business_category_id
            ):
                errors["selected_rule"] = (
                    "The selected rule does not belong to "
                    "the chosen business category."
                )

            if self.selected_rule.theme_mode != self.theme_mode:
                errors["selected_rule"] = (
                    "The selected rule theme does not match "
                    "the requested theme."
                )

        if (
            self.generated_palette_id
            and self.generated_palette.source_type
            != PaletteSource.RECOMMENDATION
        ):
            errors["generated_palette"] = (
                "The generated palette must use the source type "
                "'Recommendation'."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.session_key = self.session_key.strip()
        self.full_clean()
        return super().save(*args, **kwargs)


class RecommendationRequestAvoidedColor(TimeStampedModel):
    """
    Color family selected by a user to avoid.
    """

    recommendation_request = models.ForeignKey(
        RecommendationRequest,
        on_delete=models.CASCADE,
        related_name="avoided_color_records",
    )

    color_family = models.ForeignKey(
        "core.ColorFamily",
        on_delete=models.PROTECT,
        related_name="recommendation_request_avoidances",
    )

    class Meta:
        db_table = "recommendation_request_avoided_colors"
        ordering = ["color_family"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "recommendation_request",
                    "color_family",
                ],
                name="unique_request_avoided_color",
            ),
        ]

    def __str__(self):
        return (
            f"Request {self.recommendation_request_id} avoids "
            f"{self.color_family.name}"
        )

    def clean(self):
        super().clean()

        if (
            self.recommendation_request_id
            and self.color_family_id
            and self.recommendation_request.preferred_color_family_id
            == self.color_family_id
        ):
            raise ValidationError(
                {
                    "color_family": (
                        "The preferred color family cannot also "
                        "be selected as an avoided color."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
