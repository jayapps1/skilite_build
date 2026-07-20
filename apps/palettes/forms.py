import re

from django import forms

from apps.core.choices import ColorRole
from apps.core.models import BusinessCategory, ColorFamily
from apps.core.validators import validate_hex_color

from .models import Palette


DEFAULT_COLORS = {
    ColorRole.PRIMARY: "#2563EB",
    ColorRole.SECONDARY: "#64748B",
    ColorRole.ACCENT: "#F59E0B",
    ColorRole.BACKGROUND: "#F8FAFC",
    ColorRole.SURFACE: "#FFFFFF",
    ColorRole.HEADING: "#0F172A",
    ColorRole.BODY_TEXT: "#334155",
    ColorRole.MUTED_TEXT: "#64748B",
    ColorRole.BORDER: "#E2E8F0",
    ColorRole.SUCCESS: "#16A34A",
    ColorRole.WARNING: "#D97706",
    ColorRole.DANGER: "#DC2626",
    ColorRole.INFO: "#0284C7",
}


class PaletteEditorForm(forms.ModelForm):
    """
    Edits palette information and all 13 semantic colours
    through one Django form.
    """

    class Meta:
        model = Palette

        fields = (
            "name",
            "business_category",
            "dominant_color_family",
            "theme_mode",
            "description",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter a palette name",
                }
            ),
            "business_category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "dominant_color_family": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "theme_mode": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": (
                        "Describe the purpose of this palette"
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[
            "business_category"
        ].queryset = (
            BusinessCategory.objects
            .filter(is_active=True)
            .order_by("display_order", "name")
        )

        self.fields[
            "dominant_color_family"
        ].queryset = (
            ColorFamily.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self.fields[
            "business_category"
        ].empty_label = "Select a business category"

        self.fields[
            "dominant_color_family"
        ].empty_label = "Select the dominant colour family"

        stored_colors = {}

        if self.instance and self.instance.pk:
            stored_colors = dict(
                self.instance.colors.values_list(
                    "role",
                    "hex_value",
                )
            )

        for role, label in ColorRole.choices:
            field_name = self.get_color_field_name(role)

            self.fields[field_name] = forms.CharField(
                label=label,
                max_length=9,
                validators=[validate_hex_color],
                widget=forms.TextInput(
                    attrs={
                        "class": "form-control hex-input",
                        "data-color-role": role,
                        "autocomplete": "off",
                        "spellcheck": "false",
                        "placeholder": "#2563EB",
                    }
                ),
            )

            if not self.is_bound:
                self.initial[field_name] = stored_colors.get(
                    role,
                    DEFAULT_COLORS[role],
                )

    @staticmethod
    def get_color_field_name(role):
        return f"color_{role.lower()}"

    @property
    def color_controls(self):
        """
        Return template-ready details for every colour role.
        """

        controls = []

        for role, label in ColorRole.choices:
            field_name = self.get_color_field_name(role)
            bound_field = self[field_name]

            value = str(
                bound_field.value()
                or DEFAULT_COLORS[role]
            ).upper()

            if re.fullmatch(
                r"#[0-9A-F]{6}([0-9A-F]{2})?",
                value,
            ):
                picker_value = value[:7]
            else:
                picker_value = DEFAULT_COLORS[role][:7]

            controls.append(
                {
                    "role": role,
                    "label": label,
                    "field": bound_field,
                    "picker_value": picker_value,
                }
            )

        return controls

    def clean(self):
        cleaned_data = super().clean()

        for role in ColorRole.values:
            field_name = self.get_color_field_name(role)
            value = cleaned_data.get(field_name)

            if value:
                cleaned_data[field_name] = value.upper()

        return cleaned_data

    def get_color_map(self):
        """
        Return the validated role-to-HEX dictionary.
        """

        if not self.is_valid():
            raise ValueError(
                "The form must be valid before accessing colours."
            )

        return {
            role: self.cleaned_data[
                self.get_color_field_name(role)
            ]
            for role in ColorRole.values
        }