from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

from apps.core.choices import (
    ColorRole,
    PaletteSource,
)
from apps.core.models import BusinessCategory
from apps.palettes.models import Palette


class HomeView(TemplateView):
    """
    Public landing page for Skilite Build.
    """

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        active_categories = (
            BusinessCategory.objects
            .filter(is_active=True)
            .order_by("display_order", "name")
        )

        preset_palettes = (
            Palette.objects
            .filter(
                source_type=PaletteSource.PRESET,
                is_active=True,
            )
            .select_related(
                "business_category",
                "dominant_color_family",
            )
            .prefetch_related("colors")
            .order_by(
                "business_category__display_order",
                "name",
            )
        )

        context.update(
            {
                "featured_categories": active_categories[:8],
                "featured_presets": preset_palettes[:4],
                "category_count": active_categories.count(),
                "preset_count": preset_palettes.count(),
                "semantic_role_count": len(
                    ColorRole.values
                ),
            }
        )

        return context