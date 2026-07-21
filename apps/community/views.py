import hashlib
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView

from apps.accounts.models import log_user_activity
from apps.core.choices import (
    CopyType,
    ModerationStatus,
    PaletteSource,
    PaletteVisibility,
    ThemeMode,
)
from apps.community.models import PaletteLike, PaletteCopy, PaletteReport, PaletteView
from apps.core.models import BusinessCategory
from apps.palettes.models import Palette
from apps.palettes.services import PaletteCommunityService


class CommunityGalleryView(ListView):
    """
    Public directory of community-submitted palettes.

    Supports search, sorting, filtering by business category and theme.
    """

    model = Palette
    template_name = "community/gallery.html"
    context_object_name = "palettes"
    paginate_by = 8

    def get_queryset(self):
        # Base queryset for approved, published public palettes
        queryset = (
            Palette.objects
            .filter(
                is_published=True,
                visibility=PaletteVisibility.PUBLIC,
                moderation_status=ModerationStatus.APPROVED,
                is_active=True,
            )
            .select_related("owner", "business_category")
            .prefetch_related("colors")
            .annotate(
                likes_count=Count("likes", distinct=True),
                views_count=Count("views", distinct=True),
            )
        )

        # Filters
        category_slug = self.request.GET.get("category", "").strip()
        if category_slug:
            queryset = queryset.filter(business_category__slug=category_slug)

        theme = self.request.GET.get("theme", "").strip()
        if theme in ThemeMode.values:
            queryset = queryset.filter(theme_mode=theme)

        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(owner__username__icontains=search)
            )

        # Sorting
        sort = self.request.GET.get("sort", "newest").strip()
        if sort == "likes":
            queryset = queryset.order_by("-likes_count", "-created_at")
        elif sort == "views":
            queryset = queryset.order_by("-views_count", "-created_at")
        elif sort == "alphabetical":
            queryset = queryset.order_by("name")
        else:  # newest
            queryset = queryset.order_by("-created_at")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Inject categories that have public presets/palettes
        context["categories"] = BusinessCategory.objects.filter(is_active=True).order_by("display_order", "name")
        context["theme_choices"] = ThemeMode.choices
        context["selected_category"] = self.request.GET.get("category", "").strip()
        context["selected_theme"] = self.request.GET.get("theme", "").strip()
        context["current_search"] = self.request.GET.get("search", "").strip()
        context["current_sort"] = self.request.GET.get("sort", "newest").strip()

        # Build url parameters for pagination
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["filter_query"] = query_params.urlencode()

        # Dynamic layout inheritance
        context["extend_template"] = (
            "base/base_dashboard.html"
            if self.request.user.is_authenticated
            else "base/base.html"
        )

        # Map color values on each palette card
        for palette in context["palettes"]:
            palette.card_colors = palette.colors.all()[:13]

        # For checking if logged-in user liked the palettes on the page
        if self.request.user.is_authenticated:
            user_likes = PaletteLike.objects.filter(
                user=self.request.user,
                palette__in=context["palettes"]
            ).values_list("palette_id", flat=True)
            context["user_liked_ids"] = list(user_likes)
        else:
            context["user_liked_ids"] = []

        return context


class CopyCommunityPaletteView(LoginRequiredMixin, View):
    """
    Copies an approved public community palette to the user's private repository.
    """

    def post(self, request, slug, *args, **kwargs):
        source_palette = get_object_or_404(
            Palette.objects.filter(
                is_published=True,
                visibility=PaletteVisibility.PUBLIC,
                moderation_status=ModerationStatus.APPROVED,
                is_active=True,
            ),
            slug=slug,
        )

        try:
            copied_palette = PaletteCommunityService.copy_community_palette(
                source_palette=source_palette,
                user=request.user,
            )
            log_user_activity(
                request,
                request.user,
                "Applied Community Copy",
                f"Copied community palette '{source_palette.name}' (owner: {source_palette.owner})",
            )
            messages.success(
                request,
                f"'{source_palette.name}' has been copied to your private library.",
            )
            return redirect("palettes:edit", slug=copied_palette.slug)
        except Exception as e:
            messages.error(request, f"Error copying palette: {str(e)}")
            return redirect("community:gallery")


class PaletteLikeToggleView(LoginRequiredMixin, View):
    """
    Toggles a user like on a public community palette.

    Handles AJAX calls returning updated metrics.
    """

    def post(self, request, slug, *args, **kwargs):
        palette = get_object_or_404(
            Palette.objects.filter(
                is_published=True,
                visibility=PaletteVisibility.PUBLIC,
                moderation_status=ModerationStatus.APPROVED,
                is_active=True,
            ),
            slug=slug,
        )

        like_record = PaletteLike.objects.filter(user=request.user, palette=palette).first()
        if like_record:
            like_record.delete()
            liked = False
            details = f"Unliked public palette '{palette.name}'"
        else:
            PaletteLike.objects.create(user=request.user, palette=palette)
            liked = True
            details = f"Liked public palette '{palette.name}'"

        log_user_activity(request, request.user, "Toggled Like", details)
        likes_count = palette.likes.count()

        return JsonResponse({
            "liked": liked,
            "likes_count": likes_count,
        })


class PaletteReportView(LoginRequiredMixin, CreateView):
    """
    Allows users to report misleading or inappropriate community palettes.
    """

    model = PaletteReport
    template_name = "community/report_palette.html"
    fields = ["reason", "description"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["palette"] = get_object_or_404(Palette, slug=self.kwargs.get("slug"))
        context["extend_template"] = (
            "base/base_dashboard.html"
            if self.request.user.is_authenticated
            else "base/base.html"
        )
        return context

    def form_valid(self, form):
        palette = get_object_or_404(Palette, slug=self.kwargs.get("slug"))
        
        # User cannot report their own palette
        if palette.owner == self.request.user:
            messages.error(self.request, "You cannot report your own palette.")
            return redirect("community:gallery")

        form.instance.palette = palette
        form.instance.reported_by = self.request.user
        form.instance.status = "PENDING"
        
        response = super().form_valid(form)

        log_user_activity(
            self.request,
            self.request.user,
            "Reported Palette",
            f"Reported palette '{palette.name}' for: {form.instance.reason}",
            is_priority=True,
        )

        messages.success(
            self.request,
            "Thank you. Your report has been submitted to the moderation team.",
        )
        return response

    def get_success_url(self):
        return redirect("community:gallery").url


class TrackViewCountView(View):
    """
    Logs unique views for public palettes to prevent double-counting.
    """

    def post(self, request, slug, *args, **kwargs):
        palette = get_object_or_404(
            Palette.objects.filter(
                is_published=True,
                visibility=PaletteVisibility.PUBLIC,
                moderation_status=ModerationStatus.APPROVED,
                is_active=True,
            ),
            slug=slug,
        )

        # Get IP Hash
        ip = None
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")

        ip_hash = hashlib.sha256(ip.encode("utf-8")).hexdigest() if ip else ""
        session_key = request.session.session_key or ""
        
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        user = request.user if request.user.is_authenticated else None

        # Check if already viewed in the last hour
        time_limit = timezone.now() - timezone.timedelta(hours=1)
        recent_view = PaletteView.objects.filter(
            palette=palette,
            ip_hash=ip_hash,
            viewed_at__gte=time_limit
        )

        if not recent_view.exists():
            PaletteView.objects.create(
                palette=palette,
                user=user,
                session_key=session_key,
                ip_hash=ip_hash,
            )

        views_count = palette.views.count()
        return JsonResponse({"views_count": views_count})
