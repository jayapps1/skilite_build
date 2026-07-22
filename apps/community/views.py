import hashlib
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, DetailView

from apps.accounts.models import log_user_activity
from apps.core.choices import (
    CopyType,
    ModerationStatus,
    PaletteSource,
    PaletteVisibility,
    ThemeMode,
)
from apps.community.models import PaletteLike, PaletteCopy, PaletteReport, PaletteView, PaletteExport
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

        # For checking if user (or guest) liked the palettes on the page
        if self.request.user.is_authenticated:
            user_likes = PaletteLike.objects.filter(
                user=self.request.user,
                palette__in=context["palettes"]
            ).values_list("palette_id", flat=True)
            context["user_liked_ids"] = list(user_likes)
        else:
            session_key = self.request.session.session_key or ""
            if session_key:
                user_likes = PaletteLike.objects.filter(
                    user__isnull=True,
                    session_key=session_key,
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


class PaletteLikeToggleView(View):
    """
    Toggles a user like on a public community palette (supports anonymous guests).
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

        # Get/Save Session Key
        session_key = request.session.session_key or ""
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        if request.user.is_authenticated:
            like_record = PaletteLike.objects.filter(user=request.user, palette=palette).first()
            if like_record:
                like_record.delete()
                liked = False
                details = f"Unliked public palette '{palette.name}'"
            else:
                PaletteLike.objects.create(
                    user=request.user, 
                    palette=palette,
                    session_key=session_key,
                    ip_hash=ip_hash
                )
                liked = True
                details = f"Liked public palette '{palette.name}'"
            log_user_activity(request, request.user, "Toggled Like", details)
        else:
            like_record = PaletteLike.objects.filter(
                user__isnull=True,
                session_key=session_key,
                palette=palette
            ).first()
            if like_record:
                like_record.delete()
                liked = False
            else:
                PaletteLike.objects.create(
                    user=None,
                    palette=palette,
                    session_key=session_key,
                    ip_hash=ip_hash
                )
                liked = True

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


def record_palette_view(request, palette):
    """
    Logs unique views for public palettes to prevent double-counting.
    """
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

        record_palette_view(request, palette)

        views_count = palette.views.count()
        return JsonResponse({"views_count": views_count})


class CommunityPaletteDetailView(DetailView):
    """
    Detailed read-only website preview for a public community palette.
    """
    model = Palette
    template_name = "community/palette_detail.html"
    context_object_name = "palette"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg)
        palette = get_object_or_404(
            Palette.objects.select_related(
                "owner", "business_category", "dominant_color_family"
            ).prefetch_related("colors"),
            slug=slug,
            is_active=True
        )

        # Access check:
        # Must be public, approved, and published unless the viewer is owner or admin
        is_owner = self.request.user.is_authenticated and palette.owner == self.request.user
        is_admin = self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)
        
        is_visible = (
            palette.visibility == PaletteVisibility.PUBLIC and
            palette.is_published and
            palette.moderation_status == ModerationStatus.APPROVED
        )

        if not (is_visible or is_owner or is_admin):
            raise Http404("Palette not found or you do not have permission to view it.")

        return palette

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Record view statistics using the shared helper
        record_palette_view(request, self.object)
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        palette = self.object

        # Sort the colors in custom order for swatches listing
        from apps.core.choices import ColorRole
        color_order = {role: idx for idx, role in enumerate(ColorRole.values)}
        ordered_colors = sorted(
            palette.colors.all(),
            key=lambda c: color_order.get(c.role, 999)
        )

        # Get likes count, copies count, views count, exports count
        likes_count = palette.likes.count()
        views_count = palette.views.count()
        copies_count = palette.copy_records.count()
        exports_count = palette.export_records.count()

        # Check if the current user has liked this palette
        user_liked = False
        if self.request.user.is_authenticated:
            user_liked = palette.likes.filter(user=self.request.user).exists()
        else:
            session_key = self.request.session.session_key
            if session_key:
                user_liked = palette.likes.filter(user__isnull=True, session_key=session_key).exists()

        # Count public palettes of the creator
        if palette.owner:
            owner_public_palettes_count = Palette.objects.filter(
                owner=palette.owner,
                is_published=True,
                visibility=PaletteVisibility.PUBLIC,
                moderation_status=ModerationStatus.APPROVED,
                is_active=True
            ).count()
            is_owner = self.request.user.is_authenticated and palette.owner == self.request.user
        else:
            owner_public_palettes_count = 0
            is_owner = False

        context.update({
            "ordered_colors": ordered_colors,
            "preview_colors": {c.role: c.hex_value for c in ordered_colors},
            "likes_count": likes_count,
            "views_count": views_count,
            "copies_count": copies_count,
            "exports_count": exports_count,
            "user_liked": user_liked,
            "owner_public_palettes_count": owner_public_palettes_count,
            "is_owner": is_owner,
            "extend_template": (
                "base/base_dashboard.html"
                if self.request.user.is_authenticated
                else "base/base.html"
            )
        })

        return context


class ExportPaletteView(View):
    """
    Generates downloadable assets for the palette colors and logs the export action.
    """
    def get(self, request, slug, export_format, *args, **kwargs):
        palette = get_object_or_404(
            Palette.objects.prefetch_related("colors"),
            slug=slug,
            is_active=True
        )

        # Exporter must respect allow_export
        if not palette.allow_export:
            return HttpResponse("Exporting is disabled by the owner of this palette.", status=403)

        # Enforce view permission check (same as detail view)
        is_owner = request.user.is_authenticated and palette.owner == request.user
        is_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
        is_visible = (
            palette.visibility == PaletteVisibility.PUBLIC and
            palette.is_published and
            palette.moderation_status == ModerationStatus.APPROVED
        )

        if not (is_visible or is_owner or is_admin):
            raise Http404("Palette not found.")

        # Map colors
        color_map = {color.role: color.hex_value for color in palette.colors.all()}
        
        # Log export audit record
        session_key = request.session.session_key or ""
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        PaletteExport.objects.create(
            palette=palette,
            user=request.user if request.user.is_authenticated else None,
            export_format=export_format.upper(),
            session_key=session_key,
            palette_snapshot=color_map
        )

        log_user_activity(
            request,
            request.user if request.user.is_authenticated else None,
            "Exported Palette",
            f"Exported palette '{palette.name}' (ID: {palette.id}) in {export_format.upper()} format."
        )

        # Format content
        format_upper = export_format.upper()
        content = ""
        filename = f"palette-{palette.slug}"
        content_type = "text/plain"

        if format_upper == "CSS":
            filename += ".css"
            content_type = "text/css"
            content = ":root {\n"
            for role, hex_val in color_map.items():
                var_name = role.lower().replace("_", "-")
                content += f"  --sk-{var_name}: {hex_val};\n"
            content += "}\n"

        elif format_upper == "JSON":
            import json
            filename += ".json"
            content_type = "application/json"
            content = json.dumps(color_map, indent=4)

        elif format_upper == "SCSS":
            filename += ".scss"
            content_type = "text/x-scss"
            for role, hex_val in color_map.items():
                var_name = role.lower().replace("_", "-")
                content += f"$sk-{var_name}: {hex_val};\n"

        elif format_upper == "BOOTSTRAP":
            filename += "-bootstrap.scss"
            content_type = "text/x-scss"
            content = "// Bootstrap Variable Overrides\n"
            primary = color_map.get("PRIMARY", "#0d6efd")
            secondary = color_map.get("SECONDARY", "#6c757d")
            success = color_map.get("SUCCESS", "#198754")
            info = color_map.get("INFO", "#0dcaf0")
            warning = color_map.get("WARNING", "#ffc107")
            danger = color_map.get("DANGER", "#dc3545")
            content += f"$primary: {primary};\n"
            content += f"$secondary: {secondary};\n"
            content += f"$success: {success};\n"
            content += f"$info: {info};\n"
            content += f"$warning: {warning};\n"
            content += f"$danger: {danger};\n"

        elif format_upper == "TAILWIND":
            filename += "-tailwind.js"
            content_type = "application/javascript"
            content = "module.exports = {\n  theme: {\n    extend: {\n      colors: {\n"
            for role, hex_val in color_map.items():
                var_name = role.lower().replace("_", "-")
                content += f"        '{var_name}': '{hex_val}',\n"
            content += "      }\n    }\n  }\n}\n"

        elif format_upper == "REACT":
            filename += "-theme.js"
            content_type = "application/javascript"
            content = "export const theme = {\n"
            for role, hex_val in color_map.items():
                content += f"  {role}: '{hex_val}',\n"
            content += "};\n"

        elif format_upper == "ANDROID_COMPOSE":
            filename += "Theme.kt"
            content_type = "text/plain"
            content = "import androidx.compose.ui.graphics.Color\n\n"
            for role, hex_val in color_map.items():
                hex_clean = hex_val.strip("#")
                if len(hex_clean) == 6:
                    hex_clean = "FF" + hex_clean
                content += f"val {role} = Color(0x{hex_clean.upper()})\n"

        else:
            return HttpResponse("Unsupported export format.", status=400)

        response = HttpResponse(content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
