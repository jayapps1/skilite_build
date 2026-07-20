from django.core.exceptions import ValidationError
from django.db import transaction

from apps.core.choices import ColorRole

from .models import PaletteColor


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

        palette.save()

        for role in ColorRole.values:
            PaletteColor.objects.update_or_create(
                palette=palette,
                role=role,
                defaults={
                    "hex_value": color_map[role].upper(),
                },
            )

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
            raise ValidationError(
                "The complete palette colour system could not "
                "be saved."
            )

        return palette