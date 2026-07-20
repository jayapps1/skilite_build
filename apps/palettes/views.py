from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.views import View
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
)

from apps.core.choices import (
    ColorRole,
    ModerationStatus,
    PaletteSource,
    PaletteVisibility,
    ThemeMode,
)

from django.db.models import (
    Case,
    Count,
    IntegerField,
    Prefetch,
    Q,
    When,
)
from apps.core.models import BusinessCategory

from .forms import PaletteEditorForm
from .models import Palette, PaletteColor
from .services import (
    PaletteDuplicateService,
    PaletteEditorService,
    PaletteLifecycleService,
    PalettePresetService,
)


BUSINESS_PREVIEW_CONTENT = {
    "technology": {
        "brand": "NovaTech",
        "kicker": "Modern digital solutions",
        "headline": "Build smarter technology for your business",
        "description": (
            "Reliable software, cloud, and cybersecurity "
            "solutions for growing organisations."
        ),
        "services": [
            "Web Development",
            "Cloud Solutions",
            "Cybersecurity",
        ],
    },
    "finance": {
        "brand": "TrustCapital",
        "kicker": "Secure financial services",
        "headline": "Plan and protect your financial future",
        "description": (
            "Professional financial planning and investment "
            "services designed around your goals."
        ),
        "services": [
            "Investment Planning",
            "Business Banking",
            "Financial Advice",
        ],
    },
    "restaurant-food": {
        "brand": "Savory Kitchen",
        "kicker": "Fresh food, prepared with care",
        "headline": "Delicious meals for every occasion",
        "description": (
            "Fresh ingredients, professional catering, and "
            "convenient food delivery."
        ),
        "services": [
            "Restaurant Dining",
            "Food Delivery",
            "Event Catering",
        ],
    },
    "healthcare": {
        "brand": "CarePoint Health",
        "kicker": "Trusted healthcare services",
        "headline": "Professional care for healthier lives",
        "description": (
            "Accessible medical support and patient-focused "
            "healthcare services."
        ),
        "services": [
            "Medical Consultation",
            "Preventive Care",
            "Health Screening",
        ],
    },
    "education": {
        "brand": "BrightPath Academy",
        "kicker": "Learn, grow, and succeed",
        "headline": "Education that prepares you for the future",
        "description": (
            "Practical learning programmes designed for "
            "students, professionals, and organisations."
        ),
        "services": [
            "Online Courses",
            "Professional Training",
            "Student Support",
        ],
    },
    "beauty-cosmetics": {
        "brand": "Velora Beauty",
        "kicker": "Beauty designed around you",
        "headline": "Discover confidence in every detail",
        "description": (
            "Premium beauty treatments, cosmetics, and "
            "personal care services."
        ),
        "services": [
            "Beauty Treatments",
            "Cosmetic Products",
            "Skin Care",
        ],
    },
    "construction": {
        "brand": "SolidBuild",
        "kicker": "Built with strength and precision",
        "headline": "Construction solutions that stand the test of time",
        "description": (
            "Professional building, renovation, and project "
            "management services."
        ),
        "services": [
            "Building Construction",
            "Renovation",
            "Project Management",
        ],
    },
    "logistics-transport": {
        "brand": "SwiftRoute Logistics",
        "kicker": "Reliable movement, delivered",
        "headline": "Transport and logistics without delay",
        "description": (
            "Efficient delivery, fleet, and supply-chain "
            "services for modern businesses."
        ),
        "services": [
            "Cargo Delivery",
            "Fleet Management",
            "Supply Chain",
        ],
    },
}


class PaletteEditorContextMixin:
    template_name = "palettes/editor.html"
    form_class = PaletteEditorForm

    def get_success_url(self):
        return reverse(
            "palettes:edit",
            kwargs={
                "slug": self.object.slug,
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        preview_content = {
            "default": {
                "brand": "Your Business",
                "kicker": "Professional business services",
                "headline": (
                    "Build a stronger digital presence"
                ),
                "description": (
                    "Use your semantic colour system to preview "
                    "a realistic professional website."
                ),
                "services": [
                    "Professional Service",
                    "Customer Support",
                    "Business Solutions",
                ],
            }
        }

        categories = (
            BusinessCategory.objects
            .filter(is_active=True)
            .order_by("display_order", "name")
        )

        for category in categories:
            category_content = (
                BUSINESS_PREVIEW_CONTENT.get(
                    category.slug
                )
            )

            if category_content is None:
                category_content = {
                    "brand": category.name,
                    "kicker": (
                        f"Professional {category.name.lower()} "
                        "services"
                    ),
                    "headline": (
                        f"Grow your {category.name.lower()} "
                        "business"
                    ),
                    "description": (
                        "A flexible business preview using your "
                        "selected semantic colour system."
                    ),
                    "services": [
                        "Professional Service",
                        "Customer Support",
                        "Business Solutions",
                    ],
                }

            preview_content[str(category.pk)] = (
                category_content
            )

        context.update(
            {
                "business_preview_content": preview_content,
                "is_editing": bool(
                    getattr(self.object, "pk", None)
                ),
            }
        )

        return context

    def save_editor_form(self, form):
        try:
            self.object = PaletteEditorService.save_palette(
                palette=form.save(commit=False),
                color_map=form.get_color_map(),
            )
        except ValidationError as exc:
            form.add_error(
                None,
                " ".join(exc.messages),
            )

            return self.form_invalid(form)

        return redirect(self.get_success_url())


class PaletteCreateView(
    LoginRequiredMixin,
    PaletteEditorContextMixin,
    CreateView,
):
    model = Palette

    def get_form(self, form_class=None):
        """
        Configure protected model fields before Django validates
        the ModelForm.
        """

        form = super().get_form(form_class)

        form.instance.owner = self.request.user
        form.instance.source_palette = None
        form.instance.source_type = PaletteSource.MANUAL
        form.instance.visibility = PaletteVisibility.PRIVATE
        form.instance.moderation_status = (
            ModerationStatus.DRAFT
        )
        form.instance.allow_export = True
        form.instance.is_published = False
        form.instance.is_featured = False
        form.instance.is_active = True

        return form

    def form_valid(self, form):
        response = self.save_editor_form(form)

        if not form.errors:
            messages.success(
                self.request,
                "Your palette was created successfully.",
            )

        return response

class PaletteUpdateView(
    LoginRequiredMixin,
    PaletteEditorContextMixin,
    UpdateView,
):
    model = Palette
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Palette.objects
            .filter(
                owner=self.request.user,
                is_active=True,
            )
            .prefetch_related("colors")
        )

    def form_valid(self, form):
        response = self.save_editor_form(form)

        if not form.errors:
            messages.success(
                self.request,
                "Your palette was updated successfully.",
            )

        return response
    

class MyPaletteListView(
    LoginRequiredMixin,
    ListView,
):
    """
    Displays palettes owned by the authenticated user.

    Supports search, source-type filtering, theme filtering,
    optimized colour loading, and pagination.
    """

    model = Palette
    template_name = "palettes/my_palettes.html"
    context_object_name = "palettes"
    paginate_by = 9

    def get_queryset(self):
        queryset = (
            Palette.objects
            .filter(
                owner=self.request.user,
                is_active=True,
            )
            .select_related(
                "business_category",
                "dominant_color_family",
                "source_palette",
            )
            .prefetch_related(
                Prefetch(
                    "colors",
                    queryset=self.get_ordered_colors(),
                    to_attr="card_colors",
                )
            )
            .annotate(
                color_total=Count(
                    "colors",
                    distinct=True,
                ),
                like_total=Count(
                    "likes",
                    distinct=True,
                ),
                view_total=Count(
                    "views",
                    distinct=True,
                ),
            )
        )

        search_term = self.request.GET.get(
            "search",
            "",
        ).strip()

        source_type = self.request.GET.get(
            "source",
            "",
        ).strip()

        theme_mode = self.request.GET.get(
            "theme",
            "",
        ).strip()

        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term)
                | Q(description__icontains=search_term)
                | Q(
                    business_category__name__icontains=(
                        search_term
                    )
                )
            )

        if source_type in PaletteSource.values:
            queryset = queryset.filter(
                source_type=source_type,
            )

        valid_theme_modes = {
            choice_value
            for choice_value, _ in self.get_theme_choices()
        }

        if theme_mode in valid_theme_modes:
            queryset = queryset.filter(
                theme_mode=theme_mode,
            )

        return queryset.order_by(
            "-updated_at",
            "-created_at",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_user_palettes = Palette.objects.filter(
            owner=self.request.user,
            is_active=True,
        )

        context.update(
            {
                "total_palette_count": (
                    all_user_palettes.count()
                ),
                "manual_palette_count": (
                    all_user_palettes.filter(
                        source_type=PaletteSource.MANUAL,
                    ).count()
                ),
                "recommendation_palette_count": (
                    all_user_palettes.filter(
                        source_type=(
                            PaletteSource.RECOMMENDATION
                        ),
                    ).count()
                ),
                "copied_palette_count": (
                    all_user_palettes.filter(
                        source_type__in=[
                            PaletteSource.DUPLICATE,
                            PaletteSource.COMMUNITY_COPY,
                        ],
                    ).count()
                ),
                "source_choices": PaletteSource.choices,
                "theme_choices": self.get_theme_choices(),
                "current_search": self.request.GET.get(
                    "search",
                    "",
                ).strip(),
                "current_source": self.request.GET.get(
                    "source",
                    "",
                ).strip(),
                "current_theme": self.request.GET.get(
                    "theme",
                    "",
                ).strip(),
            }
        )

        return context

    @staticmethod
    def get_theme_choices():
        from apps.core.choices import ThemeMode

        return ThemeMode.choices

    @staticmethod
    def get_ordered_colors():
        """
        Return palette colours in semantic display order.
        """

        role_order = {
            role: position
            for position, role
            in enumerate(ColorRole.values)
        }

        ordering_conditions = [
            When(
                role=role,
                then=position,
            )
            for role, position in role_order.items()
        ]

        return (
            PaletteColor.objects
            .annotate(
                semantic_order=Case(
                    *ordering_conditions,
                    default=999,
                    output_field=IntegerField(),
                )
            )
            .order_by("semantic_order")
        )


class PresetPaletteListView(ListView):
    """
    Displays active, published, system-owned preset palettes.

    Users can filter presets by business category and theme.
    """

    model = Palette
    template_name = "palettes/presets.html"
    context_object_name = "presets"
    paginate_by = 8

    def get_queryset(self):
        queryset = (
            Palette.objects.filter(
                owner__isnull=True,
                source_type=PaletteSource.PRESET,
                visibility=PaletteVisibility.PUBLIC,
                moderation_status=ModerationStatus.APPROVED,
                is_published=True,
                is_active=True,
            )
            .select_related(
                "business_category",
                "dominant_color_family",
            )
            .prefetch_related(
                Prefetch(
                    "colors",
                    queryset=(
                        MyPaletteListView.get_ordered_colors()
                    ),
                    to_attr="preset_colors",
                )
            )
            .order_by(
                "business_category__display_order",
                "business_category__name",
                "name",
            )
        )

        category_slug = self.request.GET.get(
            "category",
            "",
        ).strip()

        theme_mode = self.request.GET.get(
            "theme",
            "",
        ).strip()

        if category_slug:
            queryset = queryset.filter(
                business_category__slug=category_slug,
            )

        if theme_mode in ThemeMode.values:
            queryset = queryset.filter(
                theme_mode=theme_mode,
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        preset_category_ids = (
            Palette.objects.filter(
                owner__isnull=True,
                source_type=PaletteSource.PRESET,
                visibility=PaletteVisibility.PUBLIC,
                moderation_status=(
                    ModerationStatus.APPROVED
                ),
                is_published=True,
                is_active=True,
            )
            .exclude(
                business_category__isnull=True,
            )
            .values_list(
                "business_category_id",
                flat=True,
            )
            .distinct()
        )

        selected_theme = self.request.GET.get(
            "theme",
            "",
        ).strip()

        query_parameters = self.request.GET.copy()
        query_parameters.pop("page", None)

        context.update(
            {
                "categories": (
                    BusinessCategory.objects.filter(
                        id__in=preset_category_ids,
                        is_active=True,
                    ).order_by(
                        "display_order",
                        "name",
                    )
                ),
                "theme_choices": ThemeMode.choices,
                "selected_category": (
                    self.request.GET.get(
                        "category",
                        "",
                    ).strip()
                ),
                "selected_theme": (
                    selected_theme
                    if selected_theme in ThemeMode.values
                    else ""
                ),
                "filter_query": query_parameters.urlencode(),
            }
        )

        return context


class ApplyPresetView(
    LoginRequiredMixin,
    View,
):
    """
    Applies a system preset through a POST-only request.
    """

    http_method_names = [
        "post",
        "options",
    ]

    def post(
        self,
        request,
        slug,
        *args,
        **kwargs,
    ):
        preset = get_object_or_404(
            (
                Palette.objects.select_related(
                    "business_category",
                    "dominant_color_family",
                ).prefetch_related("colors")
            ),
            slug=slug,
            owner__isnull=True,
            source_type=PaletteSource.PRESET,
            visibility=PaletteVisibility.PUBLIC,
            moderation_status=ModerationStatus.APPROVED,
            is_published=True,
            is_active=True,
        )

        try:
            copied_palette = (
                PalettePresetService.apply_preset(
                    preset=preset,
                    user=request.user,
                )
            )
        except ValidationError as exc:
            for error_message in exc.messages:
                messages.error(
                    request,
                    error_message,
                )

            return redirect("palettes:presets")

        messages.success(
            request,
            (
                f'"{preset.name}" was added to your palettes. '
                "You can now customize it."
            ),
        )

        return redirect(
            "palettes:edit",
            slug=copied_palette.slug,
        )

class PaletteDetailView(
    LoginRequiredMixin,
    DetailView,
):
    """
    Displays one active palette owned by the current user.
    """

    model = Palette
    template_name = "palettes/palette_detail.html"
    context_object_name = "palette"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Palette.objects
            .filter(
                owner=self.request.user,
                is_active=True,
            )
            .select_related(
                "business_category",
                "dominant_color_family",
                "source_palette",
            )
            .prefetch_related("colors")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        color_order = {
            role: position
            for position, role
            in enumerate(ColorRole.values)
        }

        ordered_colors = sorted(
            self.object.colors.all(),
            key=lambda color: color_order.get(
                color.role,
                999,
            ),
        )

        context.update(
            {
                "ordered_colors": ordered_colors,
                "preview_colors": {
                    color.role: color.hex_value
                    for color in ordered_colors
                },
            }
        )

        return context


class PaletteDuplicateView(
    LoginRequiredMixin,
    View,
):
    """
    Duplicates an owned palette through a POST request.
    """

    def post(self, request, slug):
        source_palette = get_object_or_404(
            Palette.objects.prefetch_related("colors"),
            slug=slug,
            owner=request.user,
            is_active=True,
        )

        try:
            duplicate = PaletteDuplicateService.duplicate(
                source_palette=source_palette,
                user=request.user,
            )
        except ValidationError as exc:
            messages.error(
                request,
                " ".join(exc.messages),
            )

            return redirect(
                "palettes:detail",
                slug=source_palette.slug,
            )

        messages.success(
            request,
            (
                f"'{source_palette.name}' was duplicated "
                "successfully."
            ),
        )

        return redirect(
            "palettes:edit",
            slug=duplicate.slug,
        )


class PaletteDeleteView(
    LoginRequiredMixin,
    DetailView,
):
    """
    Shows delete confirmation and performs a soft deletion.
    """

    model = Palette
    template_name = (
        "palettes/palette_confirm_delete.html"
    )
    context_object_name = "palette"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Palette.objects.filter(
            owner=self.request.user,
            is_active=True,
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        PaletteLifecycleService.soft_delete(
            palette=self.object,
        )

        messages.success(
            request,
            (
                f"'{self.object.name}' was removed from "
                "your palette library."
            ),
        )

        return redirect("palettes:my_palettes")