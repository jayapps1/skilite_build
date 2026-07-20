from django.db import models

from .validators import validate_hex_color


class TimeStampedModel(models.Model):
    """
    Abstract base model that adds creation and update timestamps.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True


class ActiveModel(TimeStampedModel):
    """
    Abstract base model for records that can be deactivated.
    """

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        abstract = True


class Language(ActiveModel):
    """
    A language supported by Skilite Build.

    Initial records will be inserted using a seeder.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    native_name = models.CharField(
        max_length=100,
    )

    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Language code, for example en, tw, gaa or fr.",
    )

    is_default = models.BooleanField(
        default=False,
    )

    class Meta:
        db_table = "languages"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["is_active"],
                name="language_active_idx",
            ),
            models.Index(
                fields=["is_default"],
                name="language_default_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.native_name


class BusinessCategory(ActiveModel):
    """
    Business sector used by presets and recommendations.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "Font Awesome or Bootstrap icon class, "
            "for example fa-solid fa-laptop-code."
        ),
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        db_table = "business_categories"
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(
                fields=["is_active", "display_order"],
                name="business_active_order_idx",
            ),
        ]
        verbose_name_plural = "Business categories"

    def __str__(self) -> str:
        return self.name


class Mood(ActiveModel):
    """
    Emotional tone selected for a palette recommendation.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "moods"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["is_active"],
                name="mood_active_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class DesignStyle(ActiveModel):
    """
    Visual design style used by the recommendation engine.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "design_styles"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["is_active"],
                name="design_style_active_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class ColorFamily(ActiveModel):
    """
    General colour family such as Blue, Green, Red or Purple.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    sample_hex = models.CharField(
        max_length=9,
        validators=[validate_hex_color],
    )

    description = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "color_families"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["is_active"],
                name="color_family_active_idx",
            ),
        ]
        verbose_name_plural = "Colour families"

    def __str__(self) -> str:
        return self.name
