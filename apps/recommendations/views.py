from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from .forms import RecommendationForm
from .models import RecommendationRequest
from .services import (
    RecommendationService,
    RecommendationServiceError,
)


class RecommendationView(
    LoginRequiredMixin,
    FormView,
):
    template_name = "recommendations/index.html"
    form_class = RecommendationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recommendation_request_id = (
            self.request.GET.get("request")
        )

        if not recommendation_request_id:
            return context

        recommendation_request = (
            RecommendationRequest.objects
            .filter(
                pk=recommendation_request_id,
                user=self.request.user,
            )
            .select_related(
                "business_category",
                "mood",
                "design_style",
                "preferred_color_family",
                "selected_rule",
                "generated_palette",
                "generated_palette__source_palette",
            )
            .prefetch_related(
                "avoided_color_families",
                "generated_palette__colors",
            )
            .first()
        )

        if not recommendation_request:
            return context

        generated_palette = (
            recommendation_request.generated_palette
        )

        context.update(
            {
                "recommendation_request": (
                    recommendation_request
                ),
                "generated_palette": generated_palette,
                "preview_colors": (
                    generated_palette.color_map
                    if generated_palette
                    else {}
                ),
            }
        )

        return context

    def form_valid(self, form):
        try:
            result = RecommendationService.generate(
                user=self.request.user,
                business_category=form.cleaned_data[
                    "business_category"
                ],
                mood=form.cleaned_data.get("mood"),
                design_style=form.cleaned_data.get(
                    "design_style"
                ),
                preferred_color_family=(
                    form.cleaned_data.get(
                        "preferred_color_family"
                    )
                ),
                avoided_color_families=(
                    form.cleaned_data.get(
                        "avoided_color_families"
                    )
                ),
                theme_mode=form.cleaned_data[
                    "theme_mode"
                ],
            )
        except RecommendationServiceError as exc:
            form.add_error(None, str(exc))

            messages.error(
                self.request,
                "The recommendation could not be generated.",
            )

            return self.form_invalid(form)

        messages.success(
            self.request,
            (
                "Your colour recommendation was generated "
                "and saved successfully."
            ),
        )

        result_url = reverse(
            "recommendations:index"
        )

        return redirect(
            f"{result_url}?request="
            f"{result.recommendation_request.pk}"
        )