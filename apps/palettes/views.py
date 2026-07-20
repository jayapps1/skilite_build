from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, UpdateView

from apps.core.choices import (
    ModerationStatus,
    PaletteSource,
    PaletteVisibility,
)
from apps.core.models import BusinessCategory

from .forms import PaletteEditorForm
from .models import Palette
from .services import PaletteEditorService


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

    def form_valid(self, form):
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