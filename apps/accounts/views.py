from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, ListView, FormView
from django.utils import timezone
from datetime import timedelta
import random
import requests
import json
import pyotp
import qrcode
import base64
from io import BytesIO
from django.contrib.auth.models import Group

from apps.palettes.models import Palette
from .models import log_user_activity, UserActivityLog, OTPCode, User
from .forms import (
    UserProfileUpdateForm,
    UserRegistrationForm,
    UserUpdateForm,
    AdminCreationForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    DashboardChangePasswordForm,
)


class UserLoginView(LoginView):
    """
    Sleek login view that redirects authenticated users and shows success feedback.
    If the user has 2FA enabled, redirects to the 2FA verification challenge.
    """

    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if user.totp_enabled:
            # Multi-factor authentication is active. Redirect to 2FA verification.
            self.request.session["pre_mfa_user_id"] = user.id
            return redirect("accounts:verify_2fa")

        # Standard authentication flow
        login(self.request, user)
        messages.success(self.request, f"Welcome back, {user.username}!")
        log_user_activity(self.request, user, "Logged In", "Successful authentication")
        return redirect(self.get_success_url())


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


class CreateAdminView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """
    Super Admin only panel to provision Staff Admins with minimal privileges.
    Sets a default password and flags must_change_password.
    """

    template_name = "accounts/create_admin.html"
    form_class = AdminCreationForm
    success_url = reverse_lazy("accounts:dashboard")

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["extend_template"] = "base/base_dashboard.html"
        return context

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        phone_number = form.cleaned_data.get("phone_number")

        # Create user
        new_admin = User.objects.create_user(
            username=username,
            email=email,
            password="SkiliteAdmin2026!",
            is_staff=True,
            is_superuser=False,
            phone_number=phone_number,
            must_change_password=True,
        )

        # Assign to Staff Admins group
        group, created = Group.objects.get_or_create(name="Staff Admins")
        new_admin.groups.add(group)

        log_user_activity(
            self.request,
            self.request.user,
            "Created Admin",
            f"Created Staff Admin user '{new_admin.username}' with minimal privileges.",
            is_priority=True,
        )

        messages.success(
            self.request,
            f"Staff Admin '{new_admin.username}' created successfully! Default password is 'SkiliteAdmin2026!'.",
        )
        return redirect(self.success_url)


class ForgotPasswordView(FormView):
    """
    Asks for registered phone number and sends a 6-digit OTP code via Arkesel SMS.
    """

    template_name = "accounts/forgot_password.html"
    form_class = ForgotPasswordForm
    success_url = reverse_lazy("accounts:verify_otp")

    def form_valid(self, form):
        phone_number = form.cleaned_data.get("phone_number").strip()
        user = User.objects.filter(phone_number=phone_number).first()

        if user:
            # Generate 6-digit OTP
            otp = str(random.randint(100000, 999999))

            # Expiration set to 5 minutes
            OTPCode.objects.create(
                user=user,
                code=otp,
                expires_at=timezone.now() + timedelta(minutes=5),
            )

            # Send OTP SMS using Arkesel REST API
            url = "https://sms.arkesel.com/api/v2/sms/send"
            headers = {
                "api-key": "cm9MRlp2dlVrQVBPRmxoV2lkRGY",
                "Content-Type": "application/json",
            }
            payload = {
                "sender": "SkiliteEnt",
                "message": f"Your Skilite Build verification code is {otp}. It will expire in 5 minutes.",
                "recipients": [phone_number],
            }

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=8)
                print(f"[Arkesel Response] Status: {response.status_code}, Body: {response.text}")
            except Exception as e:
                print(f"[Arkesel SMS Error] Failed to send: {e}")

            # Debug console print for test cases and local execution
            print(f"[SMS debug] OTP {otp} sent successfully to {phone_number}")

            self.request.session["reset_password_user_id"] = user.id
            messages.info(self.request, "A 6-digit verification code has been sent to your phone.")
            return redirect(self.success_url)

        return super().form_invalid(form)


class VerifyOTPView(TemplateView):
    """
    Renders 6-digit input cells for OTP verification.
    """

    template_name = "accounts/verify_otp.html"

    def get(self, request, *args, **kwargs):
        if "reset_password_user_id" not in request.session:
            messages.error(request, "Please enter your phone number first.")
            return redirect("accounts:forgot_password")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_id = request.session.get("reset_password_user_id")
        if not user_id:
            return redirect("accounts:forgot_password")

        user = get_object_or_404(User, id=user_id)

        # Assemble code from inputs
        digits = [
            request.POST.get("digit1", ""),
            request.POST.get("digit2", ""),
            request.POST.get("digit3", ""),
            request.POST.get("digit4", ""),
            request.POST.get("digit5", ""),
            request.POST.get("digit6", ""),
        ]
        code = "".join(digits).strip()

        # Check in DB
        otp_record = OTPCode.objects.filter(
            user=user,
            code=code,
            is_used=False,
            expires_at__gt=timezone.now(),
        ).first()

        if otp_record:
            # Mark OTP code as used
            otp_record.is_used = True
            otp_record.save()

            request.session["otp_verified"] = True
            messages.success(request, "Code verified successfully! Reset your password below.")
            return redirect("accounts:reset_password")

        # Invalid code
        messages.error(request, "Invalid or expired verification code. Please try again.")
        return self.render_to_response(self.get_context_data())


class ResetPasswordView(FormView):
    """
    Form to set new password after successful OTP verification.
    """

    template_name = "accounts/reset_password.html"
    form_class = ResetPasswordForm
    success_url = reverse_lazy("accounts:login")

    def get(self, request, *args, **kwargs):
        if not request.session.get("otp_verified") or "reset_password_user_id" not in request.session:
            messages.error(request, "Please verify your phone number first.")
            return redirect("accounts:forgot_password")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user_id = self.request.session.get("reset_password_user_id")
        user = get_object_or_404(User, id=user_id)

        new_password = form.cleaned_data.get("new_password")
        user.set_password(new_password)
        user.must_change_password = False
        user.save()

        # Clean up session
        self.request.session.pop("reset_password_user_id", None)
        self.request.session.pop("otp_verified", None)

        log_user_activity(self.request, user, "Reset Password", "Password reset successfully via SMS OTP.")

        messages.success(self.request, "Your password has been reset successfully. Please log in.")
        return redirect(self.success_url)


class ChangePasswordView(LoginRequiredMixin, FormView):
    """
    Dashboard password change view. Also satisfies must_change_password middleware.
    """

    template_name = "accounts/change_password.html"
    form_class = DashboardChangePasswordForm
    success_url = reverse_lazy("accounts:dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["extend_template"] = (
            "base/base_dashboard.html" if not self.request.user.must_change_password else "base/base.html"
        )
        return context

    def form_valid(self, form):
        user = self.request.user
        current_password = form.cleaned_data.get("current_password")
        new_password = form.cleaned_data.get("new_password")

        if not user.check_password(current_password):
            form.add_error("current_password", "Incorrect password.")
            return self.form_invalid(form)

        user.set_password(new_password)
        user.must_change_password = False
        user.save()

        # Update session auth hash to keep user logged in after password modification
        update_session_auth_hash(self.request, user)

        log_user_activity(self.request, user, "Changed Password", "Modified account password.")

        messages.success(self.request, "Your password has been changed successfully.")
        return redirect(self.success_url)


class Verify2FAView(TemplateView):
    """
    MFA Google Authenticator 2FA challenge screen during login.
    """

    template_name = "accounts/verify_2fa.html"

    def get(self, request, *args, **kwargs):
        if "pre_mfa_user_id" not in request.session:
            return redirect("accounts:login")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_id = request.session.get("pre_mfa_user_id")
        if not user_id:
            return redirect("accounts:login")

        user = get_object_or_404(User, id=user_id)
        
        # Assemble code from inputs
        digits = [
            request.POST.get("digit1", ""),
            request.POST.get("digit2", ""),
            request.POST.get("digit3", ""),
            request.POST.get("digit4", ""),
            request.POST.get("digit5", ""),
            request.POST.get("digit6", ""),
        ]
        code = "".join(digits).strip()

        # Verify using pyotp
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code):
            # Complete authentication login
            login(request, user)
            request.session.pop("pre_mfa_user_id", None)
            
            messages.success(request, f"Welcome back, {user.username}!")
            log_user_activity(request, user, "Logged In (2FA)", "Successful authentication with Google Authenticator")
            return redirect("accounts:dashboard")

        # Code verification failed
        messages.error(request, "Invalid 2FA code. Please try again.")
        return self.render_to_response(self.get_context_data())


class SecuritySettingsView(LoginRequiredMixin, TemplateView):
    """
    Dedicated view to toggle and set up Google Authenticator 2FA.
    """

    template_name = "accounts/security_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["extend_template"] = "base/base_dashboard.html"
        user = self.request.user

        if not user.totp_enabled:
            # Setup phase: generate dynamic base32 secret and QR Code
            secret = self.request.session.get("totp_secret_setup")
            if not secret:
                secret = pyotp.random_base32()
                self.request.session["totp_secret_setup"] = secret

            provisioning_url = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user.email, issuer_name="Skilite Build"
            )

            # Generate base64 PNG QR code
            qr = qrcode.QRCode(version=1, box_size=5, border=2)
            qr.add_data(provisioning_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            context["qr_code_base64"] = qr_base64
            context["secret_key"] = secret

        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        action = request.POST.get("action")

        if action == "enable":
            secret = request.session.get("totp_secret_setup")
            code = request.POST.get("totp_code", "").strip()

            if secret and code:
                totp = pyotp.TOTP(secret)
                if totp.verify(code):
                    user.totp_secret = secret
                    user.totp_enabled = True
                    user.save()

                    request.session.pop("totp_secret_setup", None)

                    log_user_activity(
                        request,
                        user,
                        "Enabled 2FA",
                        "Configured Google Authenticator successfully.",
                        is_priority=True,
                    )
                    messages.success(request, "Google Authenticator 2FA enabled successfully!")
                    return redirect("accounts:settings")

            messages.error(request, "Invalid 2FA code. Setup failed.")
            return redirect("accounts:settings")

        elif action == "disable":
            user.totp_secret = None
            user.totp_enabled = False
            user.save()

            log_user_activity(
                request,
                user,
                "Disabled 2FA",
                "Removed Google Authenticator association.",
                is_priority=True,
            )
            messages.success(request, "Google Authenticator 2FA has been disabled.")
            return redirect("accounts:settings")

        return redirect("accounts:settings")
