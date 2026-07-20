from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.community.models import PaletteCopy
from apps.core.choices import (
    ColorRole,
    CopyType,
    ModerationStatus,
    PaletteSource,
    PaletteVisibility,
    ThemeMode,
)
from apps.core.models import (
    BusinessCategory,
    ColorFamily,
)

from apps.palettes.models import (
    Palette,
    PaletteColor,
)


User = get_user_model()


class PresetPaletteWorkflowTests(TestCase):
    """
    Tests the preset gallery and Apply Preset workflow.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="presetuser",
            email="presetuser@example.com",
            password="StrongPassword123!",
        )

        cls.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="StrongPassword123!",
        )

        cls.technology_category = (
            BusinessCategory.objects.create(
                name="Technology",
                slug="technology",
                description="Technology businesses.",
                icon="fa-solid fa-microchip",
                display_order=1,
                is_active=True,
            )
        )

        cls.finance_category = (
            BusinessCategory.objects.create(
                name="Finance",
                slug="finance",
                description="Finance businesses.",
                icon="fa-solid fa-building-columns",
                display_order=2,
                is_active=True,
            )
        )

        cls.blue_family = ColorFamily.objects.create(
            name="Blue",
            slug="blue",
            sample_hex="#2563EB",
            description="Blue colour family.",
            is_active=True,
        )

        cls.green_family = ColorFamily.objects.create(
            name="Green",
            slug="green",
            sample_hex="#16A34A",
            description="Green colour family.",
            is_active=True,
        )

        cls.technology_preset = cls.create_complete_preset(
            name="Technology Professional",
            slug="technology-professional",
            category=cls.technology_category,
            color_family=cls.blue_family,
            theme_mode=ThemeMode.LIGHT,
            primary_hex="#2563EB",
        )

        cls.finance_preset = cls.create_complete_preset(
            name="Finance Trust",
            slug="finance-trust",
            category=cls.finance_category,
            color_family=cls.green_family,
            theme_mode=ThemeMode.DARK,
            primary_hex="#16A34A",
        )

        cls.inactive_preset = cls.create_complete_preset(
            name="Inactive Technology",
            slug="inactive-technology",
            category=cls.technology_category,
            color_family=cls.blue_family,
            theme_mode=ThemeMode.LIGHT,
            primary_hex="#1D4ED8",
            is_active=False,
            is_published=False,
        )

        cls.recommendation_template = (
            cls.create_complete_preset(
                name="Technology Recommendation Template",
                slug="technology-recommendation-template",
                category=cls.technology_category,
                color_family=cls.blue_family,
                theme_mode=ThemeMode.LIGHT,
                primary_hex="#3B82F6",
                source_type=(
                    PaletteSource.RECOMMENDATION_TEMPLATE
                ),
                visibility=PaletteVisibility.PRIVATE,
                is_published=False,
            )
        )

        cls.user_owned_palette = cls.create_complete_preset(
            name="User-Owned Palette",
            slug="user-owned-palette",
            category=cls.technology_category,
            color_family=cls.blue_family,
            theme_mode=ThemeMode.LIGHT,
            primary_hex="#60A5FA",
            owner=cls.other_user,
            source_type=PaletteSource.DUPLICATE,
            visibility=PaletteVisibility.PRIVATE,
            moderation_status=ModerationStatus.DRAFT,
            is_published=False,
        )

    @classmethod
    def create_complete_preset(
        cls,
        *,
        name,
        slug,
        category,
        color_family,
        theme_mode,
        primary_hex,
        owner=None,
        source_type=PaletteSource.PRESET,
        visibility=PaletteVisibility.PUBLIC,
        moderation_status=ModerationStatus.APPROVED,
        is_active=True,
        is_published=True,
    ):
        palette = Palette.objects.create(
            owner=owner,
            business_category=category,
            dominant_color_family=color_family,
            source_palette=None,
            name=name,
            slug=slug,
            description=(
                f"Complete semantic colour system for {name}."
            ),
            source_type=source_type,
            theme_mode=theme_mode,
            visibility=visibility,
            moderation_status=moderation_status,
            allow_export=True,
            is_published=is_published,
            is_featured=False,
            is_active=is_active,
            published_at=(
                timezone.now()
                if is_published
                else None
            ),
        )

        color_values = {
            ColorRole.PRIMARY: primary_hex,
            ColorRole.SECONDARY: "#0F172A",
            ColorRole.ACCENT: "#F59E0B",
            ColorRole.BACKGROUND: "#F8FAFC",
            ColorRole.SURFACE: "#FFFFFF",
            ColorRole.HEADING: "#0F172A",
            ColorRole.BODY_TEXT: "#334155",
            ColorRole.MUTED_TEXT: "#64748B",
            ColorRole.BORDER: "#CBD5E1",
            ColorRole.SUCCESS: "#16A34A",
            ColorRole.WARNING: "#D97706",
            ColorRole.DANGER: "#DC2626",
            ColorRole.INFO: "#0284C7",
        }

        PaletteColor.objects.bulk_create(
            [
                PaletteColor(
                    palette=palette,
                    role=role,
                    hex_value=color_values[role],
                )
                for role in ColorRole.values
            ]
        )

        return palette

    def test_preset_gallery_displays_only_valid_system_presets(
        self,
    ):
        response = self.client.get(
            reverse("palettes:presets")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            self.technology_preset.name,
        )

        self.assertContains(
            response,
            self.finance_preset.name,
        )

        self.assertNotContains(
            response,
            self.inactive_preset.name,
        )

        self.assertNotContains(
            response,
            self.recommendation_template.name,
        )

        self.assertNotContains(
            response,
            self.user_owned_palette.name,
        )

    def test_gallery_category_filter(self):
        response = self.client.get(
            reverse("palettes:presets"),
            {
                "category": "technology",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            self.technology_preset.name,
        )

        self.assertNotContains(
            response,
            self.finance_preset.name,
        )

    def test_gallery_theme_filter(self):
        response = self.client.get(
            reverse("palettes:presets"),
            {
                "theme": ThemeMode.DARK,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            self.finance_preset.name,
        )

        self.assertNotContains(
            response,
            self.technology_preset.name,
        )

    def test_gallery_combined_filters(self):
        response = self.client.get(
            reverse("palettes:presets"),
            {
                "category": "finance",
                "theme": ThemeMode.DARK,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            self.finance_preset.name,
        )

        self.assertNotContains(
            response,
            self.technology_preset.name,
        )

    def test_authenticated_get_to_apply_route_is_not_allowed(
        self,
    ):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "palettes:apply_preset",
                kwargs={
                    "slug": self.technology_preset.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_anonymous_user_cannot_apply_preset(self):
        response = self.client.post(
            reverse(
                "palettes:apply_preset",
                kwargs={
                    "slug": self.technology_preset.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            reverse("accounts:login"),
            response.url,
        )

        self.assertFalse(
            Palette.objects.filter(
                owner=self.user,
                source_palette=self.technology_preset,
            ).exists()
        )

    def test_apply_preset_creates_private_user_palette(self):
        self.client.force_login(self.user)

        original_color_map = {
            color.role: color.hex_value
            for color in (
                self.technology_preset.colors.all()
            )
        }

        response = self.client.post(
            reverse(
                "palettes:apply_preset",
                kwargs={
                    "slug": self.technology_preset.slug,
                },
            )
        )

        copied_palette = Palette.objects.get(
            owner=self.user,
            source_palette=self.technology_preset,
        )

        self.assertRedirects(
            response,
            reverse(
                "palettes:edit",
                kwargs={
                    "slug": copied_palette.slug,
                },
            ),
        )

        self.assertEqual(
            copied_palette.source_type,
            PaletteSource.DUPLICATE,
        )

        self.assertEqual(
            copied_palette.visibility,
            PaletteVisibility.PRIVATE,
        )

        self.assertEqual(
            copied_palette.moderation_status,
            ModerationStatus.DRAFT,
        )

        self.assertTrue(
            copied_palette.is_active
        )

        self.assertFalse(
            copied_palette.is_published
        )

        self.assertFalse(
            copied_palette.is_featured
        )

        self.assertEqual(
            copied_palette.business_category,
            self.technology_preset.business_category,
        )

        self.assertEqual(
            copied_palette.dominant_color_family,
            self.technology_preset.dominant_color_family,
        )

        self.assertEqual(
            copied_palette.theme_mode,
            self.technology_preset.theme_mode,
        )

        copied_colors = copied_palette.colors.all()

        self.assertEqual(
            copied_colors.count(),
            len(ColorRole.values),
        )

        copied_color_map = {
            color.role: color.hex_value
            for color in copied_colors
        }

        self.assertEqual(
            copied_color_map,
            original_color_map,
        )

    def test_apply_preset_creates_copy_audit_record(self):
        self.client.force_login(self.user)

        self.client.post(
            reverse(
                "palettes:apply_preset",
                kwargs={
                    "slug": self.technology_preset.slug,
                },
            )
        )

        copied_palette = Palette.objects.get(
            owner=self.user,
            source_palette=self.technology_preset,
        )

        copy_record = PaletteCopy.objects.get(
            copied_by=self.user,
            source_palette=self.technology_preset,
            destination_palette=copied_palette,
        )

        self.assertEqual(
            copy_record.copy_type,
            CopyType.PRESET_APPLY,
        )

    def test_original_system_preset_is_not_modified(self):
        self.client.force_login(self.user)

        original_name = self.technology_preset.name

        original_colors = {
            color.role: color.hex_value
            for color in (
                self.technology_preset.colors.all()
            )
        }

        self.client.post(
            reverse(
                "palettes:apply_preset",
                kwargs={
                    "slug": self.technology_preset.slug,
                },
            )
        )

        self.technology_preset.refresh_from_db()

        refreshed_colors = {
            color.role: color.hex_value
            for color in (
                self.technology_preset.colors.all()
            )
        }

        self.assertEqual(
            self.technology_preset.owner,
            None,
        )

        self.assertEqual(
            self.technology_preset.name,
            original_name,
        )

        self.assertEqual(
            refreshed_colors,
            original_colors,
        )

    def test_incomplete_preset_is_not_copied(self):
        self.client.force_login(self.user)

        self.technology_preset.colors.filter(
            role=ColorRole.INFO,
        ).delete()

        palette_count_before = Palette.objects.count()
        copy_count_before = PaletteCopy.objects.count()

        response = self.client.post(
            reverse(
                "palettes:apply_preset",
                kwargs={
                    "slug": self.technology_preset.slug,
                },
            )
        )

        self.assertRedirects(
            response,
            reverse("palettes:presets"),
        )

        self.assertEqual(
            Palette.objects.count(),
            palette_count_before,
        )

        self.assertEqual(
            PaletteCopy.objects.count(),
            copy_count_before,
        )

    def test_inactive_preset_cannot_be_applied(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "palettes:apply_preset",
                kwargs={
                    "slug": self.inactive_preset.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_system_preset_cannot_be_edited(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "palettes:edit",
                kwargs={
                    "slug": self.technology_preset.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_system_preset_cannot_be_deleted(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "palettes:delete",
                kwargs={
                    "slug": self.technology_preset.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )