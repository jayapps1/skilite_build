from django import forms

from apps.core.choices import ThemeMode
from apps.core.models import (
    BusinessCategory,
    ColorFamily,
    DesignStyle,
    Mood,
)


class RecommendationForm(forms.Form):
    business_category = forms.ModelChoiceField(
        queryset=BusinessCategory.objects.none(),
        label="Business category",
        empty_label="Select a business category",
    )

    mood = forms.ModelChoiceField(
        queryset=Mood.objects.none(),
        required=False,
        empty_label="Any mood",
    )

    design_style = forms.ModelChoiceField(
        queryset=DesignStyle.objects.none(),
        required=False,
        label="Design style",
        empty_label="Any design style",
    )

    preferred_color_family = forms.ModelChoiceField(
        queryset=ColorFamily.objects.none(),
        required=False,
        label="Preferred colour family",
        empty_label="No preferred colour",
    )

    avoided_color_families = forms.ModelMultipleChoiceField(
        queryset=ColorFamily.objects.none(),
        required=False,
        label="Colours to avoid",
        help_text=(
            "Hold Ctrl on Windows or Command on macOS "
            "to select more than one colour."
        ),
    )

    theme_mode = forms.ChoiceField(
        choices=ThemeMode.choices,
        initial=ThemeMode.LIGHT,
        label="Theme mode",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[
            "business_category"
        ].queryset = (
            BusinessCategory.objects
            .filter(is_active=True)
            .order_by("display_order", "name")
        )

        self.fields["mood"].queryset = (
            Mood.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self.fields["design_style"].queryset = (
            DesignStyle.objects
            .filter(is_active=True)
            .order_by("name")
        )

        color_family_queryset = (
            ColorFamily.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self.fields[
            "preferred_color_family"
        ].queryset = color_family_queryset

        self.fields[
            "avoided_color_families"
        ].queryset = color_family_queryset

        for field_name in [
            "business_category",
            "mood",
            "design_style",
            "preferred_color_family",
            "theme_mode",
        ]:
            self.fields[field_name].widget.attrs.update(
                {
                    "class": "form-select",
                }
            )

        self.fields[
            "avoided_color_families"
        ].widget.attrs.update(
            {
                "class": "form-select",
                "size": "6",
            }
        )

    def clean(self):
        cleaned_data = super().clean()

        preferred_color = cleaned_data.get(
            "preferred_color_family"
        )

        avoided_colors = cleaned_data.get(
            "avoided_color_families"
        )

        if (
            preferred_color
            and avoided_colors
            and preferred_color in avoided_colors
        ):
            self.add_error(
                "avoided_color_families",
                (
                    "The preferred colour family cannot also "
                    "be selected as an avoided colour."
                ),
            )

        return cleaned_data