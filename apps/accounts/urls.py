from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("activity-log/", views.ActivityLogView.as_view(), name="activity_log"),
    path("logout/", LogoutView.as_view(next_page="core:home"), name="logout"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset_password"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change_password"),
    path("verify-2fa/", views.Verify2FAView.as_view(), name="verify_2fa"),
    path("security/", views.SecuritySettingsView.as_view(), name="security_settings"),
    path("create-admin/", views.CreateAdminView.as_view(), name="create_admin"),
]
