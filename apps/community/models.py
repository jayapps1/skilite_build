from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.choices import (
    CopyType,
    ExportFormat,
    ReportStatus,
)
from apps.core.models import TimeStampedModel


class PaletteLike(TimeStampedModel):
    """
    Records a like given by a registered or anonymous user to a palette.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="palette_likes",
    )

    palette = models.ForeignKey(
        "palettes.Palette",
        on_delete=models.CASCADE,
        related_name="likes",
    )

    session_key = models.CharField(
        max_length=255,
        blank=True,
    )

    ip_hash = models.CharField(
        max_length=64,
        blank=True,
    )

    class Meta:
        db_table = "palette_likes"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "palette"],
                condition=models.Q(user__isnull=False),
                name="unique_user_palette_like_new",
            ),
            models.UniqueConstraint(
                fields=["session_key", "palette"],
                condition=models.Q(user__isnull=True) & ~models.Q(session_key=""),
                name="unique_session_palette_like",
            ),
        ]

        indexes = [
            models.Index(
                fields=["palette", "-created_at"],
                name="palette_like_palette_idx",
            ),
            models.Index(
                fields=["user", "-created_at"],
                name="palette_like_user_idx",
            ),
            models.Index(
                fields=["session_key", "-created_at"],
                name="palette_like_session_idx",
            ),
        ]

    def __str__(self):
        viewer = self.user.username if self.user else f"Guest ({self.ip_hash[:8]})"
        return f"{viewer} likes {self.palette.name}"

    def clean(self):
        super().clean()
        self.session_key = self.session_key.strip()
        if not self.user_id and not self.session_key:
            raise ValidationError(
                {
                    "session_key": (
                        "A guest palette like requires "
                        "a browser session key."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.session_key = self.session_key.strip()
        self.full_clean()
        return super().save(*args, **kwargs)


class PaletteCopyQuerySet(models.QuerySet):
    def by_user(self, user):
        return self.filter(copied_by=user)

    def from_palette(self, palette):
        return self.filter(source_palette=palette)

    def recent(self):
        return self.order_by("-created_at")


class PaletteCopy(TimeStampedModel):
    """
    Records when a user creates a new palette from another palette.

    This includes:
    - Manual duplication
    - Community copying
    - Applying a preset
    - Applying a recommendation
    """

    copied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="palette_copy_records",
    )

    source_palette = models.ForeignKey(
        "palettes.Palette",
        on_delete=models.PROTECT,
        related_name="copy_records",
    )

    destination_palette = models.OneToOneField(
        "palettes.Palette",
        on_delete=models.CASCADE,
        related_name="origin_copy_record",
    )

    copy_type = models.CharField(
        max_length=30,
        choices=CopyType.choices,
    )

    objects = PaletteCopyQuerySet.as_manager()

    class Meta:
        db_table = "palette_copies"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["copied_by", "-created_at"],
                name="palette_copy_user_idx",
            ),
            models.Index(
                fields=["source_palette", "-created_at"],
                name="palette_copy_source_idx",
            ),
            models.Index(
                fields=["copy_type", "-created_at"],
                name="palette_copy_type_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.copied_by.username} copied "
            f"{self.source_palette.name}"
        )

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.source_palette_id
            and self.destination_palette_id
            and self.source_palette_id
            == self.destination_palette_id
        ):
            errors["destination_palette"] = (
                "The destination palette cannot be the same "
                "as the source palette."
            )

        if (
            self.destination_palette_id
            and self.destination_palette.owner_id
            != self.copied_by_id
        ):
            errors["destination_palette"] = (
                "The destination palette must belong to the "
                "user who copied it."
            )

        if (
            self.destination_palette_id
            and self.destination_palette.source_palette_id
            and self.destination_palette.source_palette_id
            != self.source_palette_id
        ):
            errors["destination_palette"] = (
                "The destination palette references a different "
                "source palette."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class PaletteReportQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=ReportStatus.PENDING)

    def resolved(self):
        return self.exclude(status=ReportStatus.PENDING)


class PaletteReport(TimeStampedModel):
    """
    Report submitted against an inappropriate public palette.
    """

    palette = models.ForeignKey(
        "palettes.Palette",
        on_delete=models.CASCADE,
        related_name="reports",
    )

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_palette_reports",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_palette_reports",
    )

    reason = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
    )

    admin_note = models.TextField(
        blank=True,
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    objects = PaletteReportQuerySet.as_manager()

    class Meta:
        db_table = "palette_reports"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["reported_by", "palette"],
                name="unique_user_palette_report",
            ),
        ]

        indexes = [
            models.Index(
                fields=["palette", "status"],
                name="palette_report_palette_idx",
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="palette_report_status_idx",
            ),
            models.Index(
                fields=["reviewed_by"],
                name="palette_report_reviewer_idx",
            ),
        ]

    def __str__(self):
        return (
            f"Report against {self.palette.name} "
            f"by {self.reported_by.username}"
        )

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.palette_id
            and self.reported_by_id
            and self.palette.owner_id == self.reported_by_id
        ):
            errors["palette"] = (
                "A user cannot report their own palette."
            )

        if (
            self.status != ReportStatus.PENDING
            and not self.reviewed_by_id
        ):
            errors["reviewed_by"] = (
                "A reviewer is required when resolving a report."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if (
            self.status != ReportStatus.PENDING
            and self.reviewed_by_id
            and self.reviewed_at is None
        ):
            self.reviewed_at = timezone.now()

        if self.status == ReportStatus.PENDING:
            self.reviewed_at = None

        self.full_clean()
        return super().save(*args, **kwargs)


class PaletteExportQuerySet(models.QuerySet):
    def by_user(self, user):
        return self.filter(user=user)

    def for_palette(self, palette):
        return self.filter(palette=palette)

    def recent(self):
        return self.order_by("-created_at")


class PaletteExport(TimeStampedModel):
    """
    Records palette export activity.

    A guest export may not have a saved palette. In that case,
    the exported palette values are stored in palette_snapshot.
    """

    palette = models.ForeignKey(
        "palettes.Palette",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="export_records",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="palette_exports",
    )

    export_format = models.CharField(
        max_length=30,
        choices=ExportFormat.choices,
    )

    session_key = models.CharField(
        max_length=255,
        blank=True,
    )

    palette_snapshot = models.JSONField(
        null=True,
        blank=True,
        help_text=(
            "Stores temporary palette data for guest exports "
            "or historical audit purposes."
        ),
    )

    objects = PaletteExportQuerySet.as_manager()

    class Meta:
        db_table = "palette_exports"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["palette", "-created_at"],
                name="palette_export_palette_idx",
            ),
            models.Index(
                fields=["user", "-created_at"],
                name="palette_export_user_idx",
            ),
            models.Index(
                fields=["export_format", "-created_at"],
                name="palette_export_format_idx",
            ),
            models.Index(
                fields=["session_key", "-created_at"],
                name="palette_export_session_idx",
            ),
        ]

    def __str__(self):
        if self.palette_id:
            palette_name = self.palette.name
        else:
            palette_name = "Temporary guest palette"

        return f"{palette_name} exported as {self.export_format}"

    def clean(self):
        super().clean()

        errors = {}

        self.session_key = self.session_key.strip()

        if not self.user_id and not self.session_key:
            errors["session_key"] = (
                "A guest export requires a browser session key."
            )

        if not self.palette_id and not self.palette_snapshot:
            errors["palette_snapshot"] = (
                "A temporary export requires a palette snapshot."
            )

        if (
            self.palette_id
            and not self.palette.allow_export
        ):
            errors["palette"] = (
                "The owner of this palette has disabled exporting."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.session_key = self.session_key.strip()
        self.full_clean()
        return super().save(*args, **kwargs)


class PaletteView(models.Model):
    """
    Records a visit to a published community palette.

    The IP address should be hashed before being stored.
    """

    palette = models.ForeignKey(
        "palettes.Palette",
        on_delete=models.CASCADE,
        related_name="views",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="palette_views",
    )

    session_key = models.CharField(
        max_length=255,
        blank=True,
    )

    ip_hash = models.CharField(
        max_length=64,
        blank=True,
    )

    viewed_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "palette_views"
        ordering = ["-viewed_at"]

        indexes = [
            models.Index(
                fields=["palette", "-viewed_at"],
                name="palette_view_palette_idx",
            ),
            models.Index(
                fields=["user", "-viewed_at"],
                name="palette_view_user_idx",
            ),
            models.Index(
                fields=["session_key", "-viewed_at"],
                name="palette_view_session_idx",
            ),
        ]

    def __str__(self):
        viewer = (
            self.user.username
            if self.user_id
            else "Guest"
        )

        return f"{viewer} viewed {self.palette.name}"

    def clean(self):
        super().clean()

        self.session_key = self.session_key.strip()

        if not self.user_id and not self.session_key:
            raise ValidationError(
                {
                    "session_key": (
                        "A guest palette view requires "
                        "a browser session key."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.session_key = self.session_key.strip()
        self.full_clean()
        return super().save(*args, **kwargs)
