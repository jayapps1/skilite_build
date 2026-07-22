from django.db import models


class ThemeMode(models.TextChoices):
    LIGHT = "LIGHT", "Light"
    DARK = "DARK", "Dark"


class PaletteSource(models.TextChoices):
    MANUAL = "MANUAL", "Manual"
    PRESET = "PRESET", "Preset"
    RECOMMENDATION = "RECOMMENDATION", "Recommendation"
    RECOMMENDATION_TEMPLATE = (
        "RECOMMENDATION_TEMPLATE",
        "Recommendation Template",
    )
    COMMUNITY_COPY = "COMMUNITY_COPY", "Community Copy"
    DUPLICATE = "DUPLICATE", "Duplicate"


class PaletteVisibility(models.TextChoices):
    PRIVATE = "PRIVATE", "Private"
    PUBLIC = "PUBLIC", "Public"
    UNLISTED = "UNLISTED", "Unlisted"


class ModerationStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PENDING = "PENDING", "Pending Review"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    REMOVED = "REMOVED", "Removed"


class ColorRole(models.TextChoices):
    PRIMARY = "PRIMARY", "Primary"
    SECONDARY = "SECONDARY", "Secondary"
    ACCENT = "ACCENT", "Accent"
    BACKGROUND = "BACKGROUND", "Background"
    SURFACE = "SURFACE", "Surface"
    HEADING = "HEADING", "Heading"
    BODY_TEXT = "BODY_TEXT", "Body Text"
    MUTED_TEXT = "MUTED_TEXT", "Muted Text"
    BORDER = "BORDER", "Border"
    SUCCESS = "SUCCESS", "Success"
    WARNING = "WARNING", "Warning"
    DANGER = "DANGER", "Danger"
    INFO = "INFO", "Info"


class CopyType(models.TextChoices):
    DUPLICATE = "DUPLICATE", "Duplicate"
    COMMUNITY_COPY = "COMMUNITY_COPY", "Community Copy"
    PRESET_APPLY = "PRESET_APPLY", "Preset Apply"
    RECOMMENDATION_APPLY = (
        "RECOMMENDATION_APPLY",
        "Recommendation Apply",
    )


class ExportFormat(models.TextChoices):
    CSS = "CSS", "CSS Variables"
    JSON = "JSON", "JSON"
    SCSS = "SCSS", "SCSS"
    BOOTSTRAP = "BOOTSTRAP", "Bootstrap"
    TAILWIND = "TAILWIND", "Tailwind CSS"
    REACT = "REACT", "React Theme"
    ANDROID_COMPOSE = "ANDROID_COMPOSE", "Android Compose"


class ReportStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    REVIEWED = "REVIEWED", "Reviewed"
    DISMISSED = "DISMISSED", "Dismissed"
    ACTION_TAKEN = "ACTION_TAKEN", "Action Taken"


class TranscriptionStatus(models.TextChoices):
    UPLOADED = "UPLOADED", "Uploaded"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class TranslationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class EnquiryType(models.TextChoices):
    GENERAL = "GENERAL", "General Enquiry"
    TECHNICAL_SUPPORT = "TECHNICAL_SUPPORT", "Technical Support"
    ACCOUNT_SUPPORT = "ACCOUNT_SUPPORT", "Account Support"
    PALETTE_SUPPORT = "PALETTE_SUPPORT", "Palette Support"
    EXPORT_SUPPORT = "EXPORT_SUPPORT", "Export Support"
    BUSINESS_ENQUIRY = "BUSINESS_ENQUIRY", "Business Enquiry"
    FEEDBACK = "FEEDBACK", "Feedback"
    PARTNERSHIP = "PARTNERSHIP", "Partnership"
    OTHER = "OTHER", "Other"


class EnquiryStatus(models.TextChoices):
    NEW = "NEW", "New"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    RESOLVED = "RESOLVED", "Resolved"
    CLOSED = "CLOSED", "Closed"
    SPAM = "SPAM", "Spam"
