from django.db import models
from django.conf import settings
from django.utils import timezone
import random
import string

from apps.core.choices import EnquiryType, EnquiryStatus
from .validators import validate_hex_color


class TimeStampedModel(models.Model):
    """
    Abstract base model that adds creation and update timestamps.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True


class ActiveModel(TimeStampedModel):
    """
    Abstract base model for records that can be deactivated.
    """

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        abstract = True


class Language(ActiveModel):
    """
    A language supported by Skilite Build.

    Initial records will be inserted using a seeder.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    native_name = models.CharField(
        max_length=100,
    )

    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Language code, for example en, tw, gaa or fr.",
    )

    is_default = models.BooleanField(
        default=False,
    )

    class Meta:
        db_table = "languages"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["is_active"],
                name="language_active_idx",
            ),
            models.Index(
                fields=["is_default"],
                name="language_default_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.native_name


class BusinessCategory(ActiveModel):
    """
    Business sector used by presets and recommendations.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "Font Awesome or Bootstrap icon class, "
            "for example fa-solid fa-laptop-code."
        ),
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        db_table = "business_categories"
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(
                fields=["is_active", "display_order"],
                name="business_active_order_idx",
            ),
        ]
        verbose_name_plural = "Business categories"

    def __str__(self) -> str:
        return self.name


class Mood(ActiveModel):
    """
    Emotional tone selected for a palette recommendation.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "moods"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["is_active"],
                name="mood_active_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class DesignStyle(ActiveModel):
    """
    Visual design style used by the recommendation engine.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "design_styles"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["is_active"],
                name="design_style_active_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class ColorFamily(ActiveModel):
    """
    General colour family such as Blue, Green, Red or Purple.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    sample_hex = models.CharField(
        max_length=9,
        validators=[validate_hex_color],
    )

    description = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "color_families"
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["is_active"],
                name="color_family_active_idx",
            ),
        ]
        verbose_name_plural = "Colour families"

    def __str__(self) -> str:
        return self.name


class ContactEnquiry(TimeStampedModel):
    """
    Saves message inquiries sent from public contact forms.
    """
    enquiry_code = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contact_enquiries",
    )
    full_name = models.CharField(
        max_length=150,
    )
    email = models.EmailField()
    phone = models.CharField(
        max_length=30,
        blank=True,
    )
    subject = models.CharField(
        max_length=200,
    )
    enquiry_type = models.CharField(
        max_length=30,
        choices=EnquiryType.choices,
        default=EnquiryType.GENERAL,
    )
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=EnquiryStatus.choices,
        default=EnquiryStatus.NEW,
    )
    admin_notes = models.TextField(
        blank=True,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_contact_enquiries",
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    is_read = models.BooleanField(
        default=False,
    )

    class Meta:
        db_table = "contact_enquiries"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"], name="enquiry_status_idx"),
            models.Index(fields=["created_at"], name="enquiry_created_at_idx"),
            models.Index(fields=["email"], name="enquiry_email_idx"),
            models.Index(fields=["enquiry_type"], name="enquiry_type_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.enquiry_code} - {self.full_name} ({self.enquiry_type})"

    def save(self, *args, **kwargs):
        if not self.enquiry_code:
            # Generate prefix
            date_str = timezone.now().strftime("%Y%m%d")
            # Generate random 6 characters
            random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            code = f"ENQ-{date_str}-{random_str}"
            while ContactEnquiry.objects.filter(enquiry_code=code).exists():
                random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
                code = f"ENQ-{date_str}-{random_str}"
            self.enquiry_code = code
        super().save(*args, **kwargs)

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def mark_resolved(self):
        self.status = EnquiryStatus.RESOLVED
        if not self.responded_at:
            self.responded_at = timezone.now()
        self.save()
