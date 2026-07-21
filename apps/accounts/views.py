from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView

from apps.palettes.models import Palette
from .models import log_user_activity, UserActivityLog
from .forms import UserProfileUpdateForm, UserRegistrationForm, UserUpdateForm


class UserLoginView(LoginView):
    """
    Sleek login view that redirects authenticated users and shows success feedback.
    """

    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f"Welcome back, {user.username}!")
        log_user_activity(self.request, user, "Logged In", "Successful authentication")
        return super().form_valid(form)


class UserRegisterView(CreateView):
    """
    Custom registration view using the UserRegistrationForm.
    Logs the user in automatically after a successful sign-up.
    """

    form_class = UserRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:dashboard")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        log_user_activity(self.request, user, "Registered", "Account created successfully")
        messages.success(
            self.request,
            "Account created successfully! Welcome to Skilite Build.",
        )
        return redirect(self.success_url)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Authenticated user dashboard showing palette statistics and saved palettes.
    """

    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch user's active palettes
        user_palettes = Palette.objects.filter(
            owner=self.request.user, is_active=True
        ).order_by("-created_at")

        context["palettes"] = user_palettes
        context["total_palettes"] = user_palettes.count()
        context["public_palettes"] = user_palettes.filter(
            visibility="PUBLIC", moderation_status="APPROVED"
        ).count()
        context["private_palettes"] = user_palettes.filter(
            visibility="PRIVATE"
        ).count()
        context["recent_palettes"] = user_palettes[:5]
        context["activity_logs"] = self.request.user.activity_logs.all()[:5]
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    User profile summary view listing user profile details and their palettes.
    """

    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_palettes = Palette.objects.filter(
            owner=self.request.user, is_active=True
        ).order_by("-created_at")

        context["profile"] = self.request.user.profile
        context["palettes"] = user_palettes
        context["total_palettes"] = user_palettes.count()
        context["public_palettes"] = user_palettes.filter(
            visibility="PUBLIC"
        ).count()
        context["private_palettes"] = user_palettes.filter(
            visibility="PRIVATE"
        ).count()
        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    """
    Unified settings view allowing users to update their account and profile details.
    """

    template_name = "accounts/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "user_form" not in context:
            context["user_form"] = UserUpdateForm(instance=self.request.user)
        if "profile_form" not in context:
            context["profile_form"] = UserProfileUpdateForm(
                instance=self.request.user.profile
            )
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            log_user_activity(
                request,
                request.user,
                "Updated Profile",
                "Modified account or profile settings",
            )
            messages.success(
                request, "Your settings have been updated successfully."
            )
            return redirect("accounts:settings")

        return self.render_to_response(
            self.get_context_data(
                user_form=user_form, profile_form=profile_form
            )
        )


class ActivityLogView(LoginRequiredMixin, ListView):
    """
    Shows a complete table of the user's activity logs (limit to 50 logs).
    Highlights priority items (e.g. security warnings).
    """

    model = UserActivityLog
    template_name = "accounts/activity_log.html"
    context_object_name = "logs"

    def get_queryset(self):
        # Sort priority/breach logs to the top, then sort by date, limit to 50
        return (
            UserActivityLog.objects.filter(user=self.request.user)
            .order_by("-is_priority", "-created_at")[:50]
        )
