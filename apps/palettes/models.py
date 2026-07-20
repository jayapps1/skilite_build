from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.core.choices import (
    ColorRole,
    ModerationStatus,
    PaletteSource,
    PaletteVisibility,
    ThemeMode,
)
from apps.core.models import TimeStampedModel
from apps.core.validators import validate_hex_color


class PaletteQuerySet(models.QuerySet):
    """
    Reusable queries for retrieving palettes.
    """

    def active(self):
        return self.filter(is_active=True)

    def owned_by(self, user):
        return self.filter(
            owner=user,
            is_active=True,
        )

    def published(self):
        return self.filter(
            is_active=True,
            is_published=True,
            visibility=PaletteVisibility.PUBLIC,
            moderation_status=ModerationStatus.APPROVED,
        )

    def presets(self):
        return self.filter(
            is_active=True,
            source_type=PaletteSource.PRESET,
        )

    def recommendation_templates(self):
        return self.filter(
            is_active=True,
            source_type=PaletteSource.RECOMMENDATION_TEMPLATE,
        )


class Palette(TimeStampedModel):
    """
    Central colour palette entity.

    Manual palettes, presets, recommendation templates,
    recommendation results, community copies, and duplicates
    are all stored in this model.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="palettes",
        help_text=(
            "The owner may be empty for system presets "
            "and recommendation templates."
        ),
    )

    business_category = models.ForeignKey(
        "core.BusinessCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="palettes",
    )

    dominant_color_family = models.ForeignKey(
        "core.ColorFamily",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dominant_palettes",
    )

    source_palette = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_palettes",
        help_text=(
            "Original palette when this palette was copied, "
            "duplicated, or generated from a template."
        ),
    )

    name = models.CharField(
        max_length=150,
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        blank=True,
        help_text=(
            "Leave empty to generate the slug automatically."
        ),
    )

    description = models.TextField(
        blank=True,
    )

    source_type = models.CharField(
        max_length=30,
        choices=PaletteSource.choices,
        default=PaletteSource.MANUAL,
    )

    theme_mode = models.CharField(
        max_length=10,
        choices=ThemeMode.choices,
        default=ThemeMode.LIGHT,
    )

    visibility = models.CharField(
        max_length=10,
        choices=PaletteVisibility.choices,
        default=PaletteVisibility.PRIVATE,
    )

    moderation_status = models.CharField(
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.DRAFT,
    )

    allow_export = models.BooleanField(
        default=True,
    )

    is_published = models.BooleanField(
        default=False,
    )

    is_featured = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    objects = PaletteQuerySet.as_manager()

    class Meta:
        db_table = "palettes"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["owner", "-created_at"],
                name="palette_owner_created_idx",
            ),
            models.Index(
                fields=["business_category"],
                name="palette_business_idx",
            ),
            models.Index(
                fields=["dominant_color_family"],
                name="palette_color_family_idx",
            ),
            models.Index(
                fields=["source_palette"],
                name="palette_source_palette_idx",
            ),
            models.Index(
                fields=["source_type"],
                name="palette_source_type_idx",
            ),
            models.Index(
                fields=["theme_mode"],
                name="palette_theme_idx",
            ),
            models.Index(
                fields=[
                    "visibility",
                    "moderation_status",
                    "is_published",
                ],
                name="palette_gallery_idx",
            ),
            models.Index(
                fields=["is_featured", "is_active"],
                name="palette_featured_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(is_published=False)
                    | ~models.Q(
                        visibility=PaletteVisibility.PRIVATE
                    )
                ),
                name="palette_published_not_private",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(is_featured=False)
                    | (
                        models.Q(is_published=True)
                        & models.Q(
                            moderation_status=(
                                ModerationStatus.APPROVED
                            )
                        )
                    )
                ),
                name="palette_featured_is_approved",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self):
        """
        Validate business rules that cannot be represented by
        individual database columns.
        """

        super().clean()

        errors = {}

        system_sources = {
            PaletteSource.PRESET,
            PaletteSource.RECOMMENDATION_TEMPLATE,
        }

        user_sources = {
            PaletteSource.MANUAL,
            PaletteSource.RECOMMENDATION,
            PaletteSource.COMMUNITY_COPY,
            PaletteSource.DUPLICATE,
        }

        if self.source_type in user_sources and not self.owner_id:
            errors["owner"] = (
                "This type of palette must belong to a user."
            )

        if (
            self.source_type in system_sources
            and self.visibility == PaletteVisibility.PRIVATE
        ):
            errors["visibility"] = (
                "System presets and recommendation templates "
                "cannot use private visibility."
            )

        if (
            self.source_type
            in {
                PaletteSource.COMMUNITY_COPY,
                PaletteSource.DUPLICATE,
            }
            and not self.source_palette_id
        ):
            errors["source_palette"] = (
                "Copied and duplicated palettes require "
                "an original source palette."
            )

        if (
            self.pk
            and self.source_palette_id
            and self.source_palette_id == self.pk
        ):
            errors["source_palette"] = (
                "A palette cannot use itself as its source."
            )

        if (
            self.is_published
            and self.visibility == PaletteVisibility.PRIVATE
        ):
            errors["visibility"] = (
                "A published palette cannot remain private."
            )

        if (
            self.is_featured
            and not self.is_published
        ):
            errors["is_featured"] = (
                "Only published palettes can be featured."
            )

        if (
            self.is_featured
            and self.moderation_status
            != ModerationStatus.APPROVED
        ):
            errors["moderation_status"] = (
                "Only approved palettes can be featured."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()

        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()

        self.full_clean()

        super().save(*args, **kwargs)

    def generate_unique_slug(self) -> str:
        """
        Generate a unique URL-safe slug from the palette name.
        """

        base_slug = slugify(self.name) or "palette"
        base_slug = base_slug[:180]

        candidate = base_slug
        counter = 2

        queryset = Palette.objects.all()

        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        while queryset.filter(slug=candidate).exists():
            suffix = f"-{counter}"

            candidate = (
                f"{base_slug[:180 - len(suffix)]}{suffix}"
            )

            counter += 1

        return candidate

    @property
    def color_map(self) -> dict[str, str]:
        """
        Return the palette colours as a role-to-HEX dictionary.
        """

        return {
            color.role: color.hex_value
            for color in self.colors.all()
        }

    @property
    def color_count(self) -> int:
        return self.colors.count()


class PaletteColor(TimeStampedModel):
    """
    One semantic colour belonging to a palette.

    A palette can have only one colour for each semantic role.
    """

    palette = models.ForeignKey(
        Palette,
        on_delete=models.CASCADE,
        related_name="colors",
    )

    role = models.CharField(
        max_length=20,
        choices=ColorRole.choices,
    )

    hex_value = models.CharField(
        max_length=9,
        validators=[validate_hex_color],
    )

    class Meta:
        db_table = "palette_colors"
        ordering = ["role"]

        constraints = [
            models.UniqueConstraint(
                fields=["palette", "role"],
                name="unique_palette_color_role",
            ),
        ]

        indexes = [
            models.Index(
                fields=["palette"],
                name="palette_color_palette_idx",
            ),
            models.Index(
                fields=["role"],
                name="palette_color_role_idx",
            ),
        ]

        verbose_name = "Palette colour"
        verbose_name_plural = "Palette colours"

    def __str__(self) -> str:
        return (
            f"{self.palette.name} — "
            f"{self.get_role_display()}: {self.hex_value}"
        )

    def save(self, *args, **kwargs):
        self.hex_value = self.hex_value.upper()

        self.full_clean()

        super().save(*args, **kwargs)
