from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.community.models import PaletteCopy
from apps.core.choices import (
    ColorRole,
    CopyType,
    ModerationStatus,
    PaletteSource,
    PaletteVisibility,
)

from .models import Palette, PaletteColor


class PaletteEditorService:
    """
    Saves a palette and synchronizes its complete semantic
    colour system.
    """

    @classmethod
    @transaction.atomic
    def save_palette(
        cls,
        *,
        palette,
        color_map,
    ):
        """
        Save a palette and ensure it contains exactly one colour
        for every supported semantic colour role.
        """

        expected_roles = set(ColorRole.values)
        supplied_roles = set(color_map.keys())

        missing_roles = sorted(
            expected_roles - supplied_roles
        )

        unexpected_roles = sorted(
            supplied_roles - expected_roles
        )

        if missing_roles or unexpected_roles:
            raise ValidationError(
                (
                    "The palette must contain all 13 semantic "
                    f"colour roles. Missing: {missing_roles}. "
                    f"Unexpected: {unexpected_roles}."
                )
            )

        # Run model-level validation before saving.
        palette.full_clean()
        palette.save()

        for role in ColorRole.values:
            hex_value = str(
                color_map[role]
            ).strip().upper()

            PaletteColor.objects.update_or_create(
                palette=palette,
                role=role,
                defaults={
                    "hex_value": hex_value,
                },
            )

        # Defensive cleanup in case an invalid historical role
        # exists in the database.
        PaletteColor.objects.filter(
            palette=palette,
        ).exclude(
            role__in=expected_roles,
        ).delete()

        saved_roles = set(
            PaletteColor.objects.filter(
                palette=palette,
            ).values_list(
                "role",
                flat=True,
            )
        )

        if saved_roles != expected_roles:
            missing_after_save = sorted(
                expected_roles - saved_roles
            )

            unexpected_after_save = sorted(
                saved_roles - expected_roles
            )

            raise ValidationError(
                (
                    "The complete palette colour system could "
                    "not be saved. "
                    f"Missing: {missing_after_save}. "
                    f"Unexpected: {unexpected_after_save}."
                )
            )

        return palette


class PaletteDuplicateService:
    """
    Creates a private user-owned duplicate of an existing palette.
    """

    @classmethod
    @transaction.atomic
    def duplicate(
        cls,
        *,
        source_palette,
        user,
    ):
        """
        Duplicate an active palette for an authenticated user.

        Ordinary duplicates use:
        - PaletteSource.DUPLICATE
        - CopyType.DUPLICATE
        """

        cls._validate_authenticated_user(user)

        if source_palette is None:
            raise ValidationError(
                "A source palette is required."
            )

        if not source_palette.is_active:
            raise ValidationError(
                "An inactive palette cannot be duplicated."
            )

        color_map = cls._get_complete_color_map(
            source_palette
        )

        duplicate_name = cls._build_palette_name(
            prefix="Copy of",
            source_palette=source_palette,
        )

        destination_palette = cls._create_destination_palette(
            source_palette=source_palette,
            user=user,
            name=duplicate_name,
        )

        cls._copy_palette_colors(
            destination_palette=destination_palette,
            color_map=color_map,
        )

        cls._create_copy_record(
            copied_by=user,
            source_palette=source_palette,
            destination_palette=destination_palette,
            copy_type=CopyType.DUPLICATE,
        )

        return destination_palette

    @staticmethod
    def _validate_authenticated_user(user):
        if user is None or not user.is_authenticated:
            raise ValidationError(
                "A signed-in user is required."
            )

    @staticmethod
    def _get_complete_color_map(source_palette):
        color_map = {
            color.role: color.hex_value.upper()
            for color in source_palette.colors.all()
        }

        expected_roles = set(ColorRole.values)
        actual_roles = set(color_map.keys())

        missing_roles = sorted(
            expected_roles - actual_roles
        )

        unexpected_roles = sorted(
            actual_roles - expected_roles
        )

        if (
            len(color_map) != len(expected_roles)
            or missing_roles
            or unexpected_roles
        ):
            raise ValidationError(
                (
                    "The source palette is incomplete and cannot "
                    "be duplicated. "
                    f"Missing roles: {missing_roles}. "
                    f"Unexpected roles: {unexpected_roles}."
                )
            )

        return color_map

    @staticmethod
    def _build_palette_name(
        *,
        prefix,
        source_palette,
    ):
        name_field = Palette._meta.get_field("name")
        max_length = name_field.max_length or 150

        generated_name = (
            f"{prefix} {source_palette.name}"
        )

        return generated_name[:max_length]

    @staticmethod
    def _create_destination_palette(
        *,
        source_palette,
        user,
        name,
    ):
        destination_palette = Palette(
            owner=user,
            business_category=(
                source_palette.business_category
            ),
            dominant_color_family=(
                source_palette.dominant_color_family
            ),
            source_palette=source_palette,
            name=name,
            slug="",
            description=source_palette.description,
            source_type=PaletteSource.DUPLICATE,
            theme_mode=source_palette.theme_mode,
            visibility=PaletteVisibility.PRIVATE,
            moderation_status=ModerationStatus.DRAFT,
            allow_export=True,
            is_published=False,
            is_featured=False,
            is_active=True,
            published_at=None,
        )

        destination_palette.full_clean()
        destination_palette.save()

        return destination_palette

    @staticmethod
    def _copy_palette_colors(
        *,
        destination_palette,
        color_map,
    ):
        palette_colors = [
            PaletteColor(
                palette=destination_palette,
                role=role,
                hex_value=color_map[role],
            )
            for role in ColorRole.values
        ]

        # bulk_create does not call full_clean, so validate
        # each object before inserting it.
        for palette_color in palette_colors:
            palette_color.full_clean()

        PaletteColor.objects.bulk_create(
            palette_colors
        )

        saved_count = PaletteColor.objects.filter(
            palette=destination_palette,
        ).count()

        if saved_count != len(ColorRole.values):
            raise ValidationError(
                (
                    "The duplicated palette did not receive all "
                    "13 semantic colour roles."
                )
            )

    @staticmethod
    def _create_copy_record(
        *,
        copied_by,
        source_palette,
        destination_palette,
        copy_type,
    ):
        copy_record = PaletteCopy(
            copied_by=copied_by,
            source_palette=source_palette,
            destination_palette=destination_palette,
            copy_type=copy_type,
        )

        copy_record.full_clean()
        copy_record.save()

        return copy_record


class PalettePresetService:
    """
    Applies a protected system preset to an authenticated user.

    The system preset itself is never changed. A new private,
    user-owned palette is created from the preset.
    """

    @classmethod
    @transaction.atomic
    def apply_preset(
        cls,
        *,
        preset,
        user,
    ):
        """
        Copy a complete system preset into a new editable palette.

        The copied palette uses PaletteSource.DUPLICATE because
        there is currently no dedicated PRESET_COPY source.

        The PaletteCopy audit record uses CopyType.PRESET_APPLY.
        """

        PaletteDuplicateService._validate_authenticated_user(
            user
        )

        if preset is None or not getattr(
            preset,
            "pk",
            None,
        ):
            raise ValidationError(
                "A valid preset palette is required."
            )

        try:
            system_preset = (
                Palette.objects
                .select_related(
                    "business_category",
                    "dominant_color_family",
                )
                .get(pk=preset.pk)
            )
        except Palette.DoesNotExist as exc:
            raise ValidationError(
                "The selected preset palette no longer exists."
            ) from exc

        cls._validate_system_preset(
            system_preset
        )

        color_map = (
            PaletteDuplicateService
            ._get_complete_color_map(
                system_preset
            )
        )

        destination_name = (
            PaletteDuplicateService
            ._build_palette_name(
                prefix="My",
                source_palette=system_preset,
            )
        )

        destination_palette = (
            PaletteDuplicateService
            ._create_destination_palette(
                source_palette=system_preset,
                user=user,
                name=destination_name,
            )
        )

        PaletteDuplicateService._copy_palette_colors(
            destination_palette=destination_palette,
            color_map=color_map,
        )

        PaletteDuplicateService._create_copy_record(
            copied_by=user,
            source_palette=system_preset,
            destination_palette=destination_palette,
            copy_type=CopyType.PRESET_APPLY,
        )

        return destination_palette

    @staticmethod
    def _validate_system_preset(preset):
        """
        Confirm that the selected record is an active,
        system-owned preset palette.
        """

        if preset.owner_id is not None:
            raise ValidationError(
                (
                    "Only system-owned preset palettes can "
                    "be applied."
                )
            )

        if preset.source_type != PaletteSource.PRESET:
            raise ValidationError(
                "The selected palette is not a preset palette."
            )

        if not preset.is_active:
            raise ValidationError(
                (
                    "The selected preset palette is currently "
                    "unavailable."
                )
            )


class PaletteLifecycleService:
    """
    Handles palette lifecycle operations.
    """

    @classmethod
    @transaction.atomic
    def soft_delete(
        cls,
        *,
        palette,
    ):
        """
        Soft-delete a user palette without removing its database
        record.
        """

        if palette is None:
            raise ValidationError(
                "A palette is required."
            )

        # System palettes must never be deleted through the
        # normal palette lifecycle workflow.
        if palette.owner_id is None:
            raise ValidationError(
                "System palettes cannot be deleted."
            )

        palette.is_active = False
        palette.is_published = False
        palette.is_featured = False
        palette.visibility = PaletteVisibility.PRIVATE
        palette.moderation_status = (
            ModerationStatus.REMOVED
        )
        palette.published_at = None
        palette.deleted_at = timezone.now()

        palette.full_clean()
        palette.save(
            update_fields=[
                "is_active",
                "is_published",
                "is_featured",
                "visibility",
                "moderation_status",
                "published_at",
                "deleted_at",
                "updated_at",
            ]
        )

        return palette

    @classmethod
    @transaction.atomic
    def restore(
        cls,
        *,
        palette,
    ):
        """
        Restore a soft-deleted user palette from the recycle bin.
        """
        if palette is None:
            raise ValidationError(
                "A palette is required."
            )

        palette.is_active = True
        palette.deleted_at = None
        palette.moderation_status = ModerationStatus.DRAFT

        palette.full_clean()
        palette.save(
            update_fields=[
                "is_active",
                "deleted_at",
                "moderation_status",
                "updated_at",
            ]
        )

        return palette


class PaletteCommunityService:
    """
    Handles duplication of public community palettes into private user copies.
    """

    @classmethod
    @transaction.atomic
    def copy_community_palette(
        cls,
        *,
        source_palette,
        user,
    ):
        """
        Copy an active, published public palette for an authenticated user.

        The created palette uses PaletteSource.COMMUNITY_COPY.
        The copy record uses CopyType.COMMUNITY_COPY.
        """
        PaletteDuplicateService._validate_authenticated_user(user)

        if source_palette is None:
            raise ValidationError(
                "A source palette is required."
            )

        if not source_palette.is_active or not source_palette.is_published:
            raise ValidationError(
                "An inactive or private palette cannot be copied."
            )

        color_map = (
            PaletteDuplicateService
            ._get_complete_color_map(
                source_palette
            )
        )

        destination_name = (
            PaletteDuplicateService
            ._build_palette_name(
                prefix="Copy of",
                source_palette=source_palette,
            )
        )

        destination_palette = Palette(
            owner=user,
            business_category=(
                source_palette.business_category
            ),
            dominant_color_family=(
                source_palette.dominant_color_family
            ),
            source_palette=source_palette,
            name=destination_name,
            slug="",
            description=source_palette.description,
            source_type=PaletteSource.COMMUNITY_COPY,
            theme_mode=source_palette.theme_mode,
            visibility=PaletteVisibility.PRIVATE,
            moderation_status=ModerationStatus.DRAFT,
            allow_export=True,
            is_published=False,
            is_featured=False,
            is_active=True,
            published_at=None,
        )

        destination_palette.full_clean()
        destination_palette.save()

        PaletteDuplicateService._copy_palette_colors(
            destination_palette=destination_palette,
            color_map=color_map,
        )

        PaletteDuplicateService._create_copy_record(
            copied_by=user,
            source_palette=source_palette,
            destination_palette=destination_palette,
            copy_type=CopyType.COMMUNITY_COPY,
        )

        return destination_palette