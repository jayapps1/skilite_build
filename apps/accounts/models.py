from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.choices import ThemeMode
from apps.core.models import TimeStampedModel


class User(AbstractUser):
    """
    Authentication user for Skilite Build.

    Username is currently used for login.
    Email addresses must be unique.
    """

    email = models.EmailField(
        max_length=254,
        unique=True,
    )

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(
                fields=["email"],
                name="user_email_idx",
            ),
            models.Index(
                fields=["is_active"],
                name="user_active_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.username


class UserProfile(TimeStampedModel):
    """
    Additional information belonging to one user account.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    preferred_language = models.ForeignKey(
        "core.Language",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles",
    )

    display_name = models.CharField(
        max_length=150,
        blank=True,
    )

    bio = models.TextField(
        blank=True,
    )

    profile_image = models.ImageField(
        upload_to="profile_images/%Y/%m/",
        null=True,
        blank=True,
    )

    company_name = models.CharField(
        max_length=200,
        blank=True,
    )

    website_url = models.URLField(
        max_length=500,
        blank=True,
    )

    preferred_theme = models.CharField(
        max_length=10,
        choices=ThemeMode.choices,
        default=ThemeMode.LIGHT,
    )

    class Meta:
        db_table = "user_profiles"
        indexes = [
            models.Index(
                fields=["preferred_language"],
                name="profile_language_idx",
            ),
            models.Index(
                fields=["preferred_theme"],
                name="profile_theme_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.display_name or self.user.username


class UserActivityLog(TimeStampedModel):
    """
    Log of actions taken by a user for auditing and activity tracking.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_priority = models.BooleanField(default=False)

    class Meta:
        db_table = "user_activity_logs"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.action} at {self.created_at}"


def log_user_activity(request, user, action, details="", is_priority=False):
    """
    Utility helper to log user audit actions.
    """
    if not user or not user.is_authenticated:
        return None

    ip = None
    if request:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")

    return UserActivityLog.objects.create(
        user=user,
        action=action,
        details=details,
        ip_address=ip,
        is_priority=is_priority,
    )
