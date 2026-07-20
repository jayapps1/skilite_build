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
