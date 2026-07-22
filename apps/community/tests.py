from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.core.choices import ColorRole, ModerationStatus, PaletteVisibility, CopyType
from apps.community.models import PaletteLike, PaletteCopy, PaletteReport, PaletteView
from apps.palettes.models import Palette, PaletteColor

User = get_user_model()


class CommunityGalleryTests(TestCase):
    """
    Test suite for the Community Gallery and engagement interactions.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="Password123!", email="user1@example.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="Password123!", email="user2@example.com"
        )

        # Create published palette
        self.public_palette = self.create_complete_palette(
            name="Public Palette 1",
            owner=self.user1,
            visibility=PaletteVisibility.PUBLIC,
            is_published=True,
        )

        # Create private palette
        self.private_palette = self.create_complete_palette(
            name="Private Palette 1",
            owner=self.user1,
            visibility=PaletteVisibility.PRIVATE,
            is_published=False,
        )

    def create_complete_palette(self, name, owner, visibility, is_published=True):
        palette = Palette.objects.create(
            name=name,
            owner=owner,
            visibility=visibility,
            is_published=is_published,
            moderation_status=ModerationStatus.APPROVED,
        )
        for role in ColorRole.values:
            PaletteColor.objects.create(
                palette=palette,
                role=role,
                hex_value="#123456",
            )
        return palette

    def test_gallery_lists_only_approved_public_palettes(self):
        """
        Verify that the gallery view only displays public, approved palettes.
        """
        url = reverse("community:gallery")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public Palette 1")
        self.assertNotContains(response, "Private Palette 1")

    def test_like_toggle_ajax(self):
        """
        Verify that POSTing to the like toggle view likes/unlikes a palette.
        """
        self.client.login(username="user2", password="Password123!")
        url = reverse("community:like", kwargs={"slug": self.public_palette.slug})
        
        # Like
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["liked"], True)
        self.assertEqual(response.json()["likes_count"], 1)
        self.assertEqual(PaletteLike.objects.filter(palette=self.public_palette).count(), 1)

        # Unlike
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["liked"], False)
        self.assertEqual(response.json()["likes_count"], 0)
        self.assertEqual(PaletteLike.objects.filter(palette=self.public_palette).count(), 0)

    def test_copy_community_palette(self):
        """
        Verify that copying a public palette duplicates it into the user's library.
        """
        self.client.login(username="user2", password="Password123!")
        url = reverse("community:copy", kwargs={"slug": self.public_palette.slug})
        
        response = self.client.post(url)
        # Should redirect to the editor for the copied palette
        self.assertEqual(response.status_code, 302)
        
        copies = Palette.objects.filter(owner=self.user2)
        self.assertEqual(copies.count(), 1)
        copied = copies.first()
        self.assertEqual(copied.name, "Copy of Public Palette 1")
        
        # Verify a PaletteCopy record is created
        self.assertEqual(
            PaletteCopy.objects.filter(
                copied_by=self.user2,
                source_palette=self.public_palette,
                destination_palette=copied,
                copy_type=CopyType.COMMUNITY_COPY,
            ).count(),
            1
        )

    def test_report_community_palette(self):
        """
        Verify that users can submit a report against inappropriate palettes.
        """
        self.client.login(username="user2", password="Password123!")
        url = reverse("community:report", kwargs={"slug": self.public_palette.slug})
        
        # Access report page
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Post report form
        data = {
            "reason": "Misleading colors or category match",
            "description": "The colors selected are highly illegible.",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        reports = PaletteReport.objects.filter(palette=self.public_palette)
        self.assertEqual(reports.count(), 1)
        report = reports.first()
        self.assertEqual(report.reported_by, self.user2)
        self.assertEqual(report.reason, "Misleading colors or category match")

    def test_track_views_ajax(self):
        """
        Verify that unique view hits are logged correctly.
        """
        url = reverse("community:track_view", kwargs={"slug": self.public_palette.slug})
        
        # Initial view
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["views_count"], 1)
        self.assertEqual(PaletteView.objects.filter(palette=self.public_palette).count(), 1)

        # Double views by same client session/IP should not increment count
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["views_count"], 1)
        self.assertEqual(PaletteView.objects.filter(palette=self.public_palette).count(), 1)

    def test_like_toggle_anonymous_ajax(self):
        """
        Verify that unauthenticated users can successfully toggle a like.
        """
        url = reverse("community:like", kwargs={"slug": self.public_palette.slug})
        
        # Like
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["liked"], True)
        self.assertEqual(response.json()["likes_count"], 1)
        self.assertEqual(PaletteLike.objects.filter(palette=self.public_palette, user__isnull=True).count(), 1)

        # Unlike
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["liked"], False)
        self.assertEqual(response.json()["likes_count"], 0)
        self.assertEqual(PaletteLike.objects.filter(palette=self.public_palette, user__isnull=True).count(), 0)

    def test_public_approved_palette_detail_loads(self):
        """1. Public approved palette detail loads successfully."""
        url = reverse("community:palette_detail", kwargs={"slug": self.public_palette.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.public_palette.name)

    def test_private_palette_detail_returns_404_unauthorized(self):
        """2. Private palette detail returns 404 for unauthorized users."""
        url = reverse("community:palette_detail", kwargs={"slug": self.private_palette.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_unapproved_palette_detail_returns_404_normal_visitor(self):
        """3. Unapproved palette detail returns 404 for normal visitors."""
        unapproved = self.create_complete_palette(
            name="Unapproved Public",
            owner=self.user1,
            visibility=PaletteVisibility.PUBLIC,
            is_published=True,
        )
        unapproved.moderation_status = ModerationStatus.REJECTED
        unapproved.save()
        url = reverse("community:palette_detail", kwargs={"slug": unapproved.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_palette_owner_can_access_own_private_detail(self):
        """4. Palette owner can access permitted owner views (like private palettes)."""
        self.client.login(username="user1", password="Password123!")
        url = reverse("community:palette_detail", kwargs={"slug": self.private_palette.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.private_palette.name)

    def test_community_detail_includes_all_13_colors(self):
        """5. Community detail includes all 13 colors in swatches."""
        url = reverse("community:palette_detail", kwargs={"slug": self.public_palette.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Verify 13 swatches exist in ordered_colors context
        self.assertEqual(len(response.context["ordered_colors"]), 13)

    def test_community_detail_includes_preview_configuration(self):
        """6. Community detail includes preview configuration."""
        url = reverse("community:palette_detail", kwargs={"slug": self.public_palette.slug})
        response = self.client.get(url)
        self.assertIn("preview_colors", response.context)
        self.assertEqual(len(response.context["preview_colors"]), 13)

    def test_copy_action_requires_post(self):
        """7. Copy action requires POST."""
        self.client.login(username="user2", password="Password123!")
        url = reverse("community:copy", kwargs={"slug": self.public_palette.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405) # Method Not Allowed

    def test_copy_action_requires_authentication(self):
        """8. Copy action requires authentication (redirects to login)."""
        url = reverse("community:copy", kwargs={"slug": self.public_palette.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_copy_action_creates_private_user_palette(self):
        """9. Copy action creates a private user-owned palette."""
        self.client.login(username="user2", password="Password123!")
        url = reverse("community:copy", kwargs={"slug": self.public_palette.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        copied = Palette.objects.filter(owner=self.user2).first()
        self.assertEqual(copied.visibility, PaletteVisibility.PRIVATE)

    def test_copy_action_copies_all_13_colors(self):
        """10. Copy action copies all 13 colors."""
        self.client.login(username="user2", password="Password123!")
        url = reverse("community:copy", kwargs={"slug": self.public_palette.slug})
        self.client.post(url)
        copied = Palette.objects.filter(owner=self.user2).first()
        self.assertEqual(copied.colors.count(), 13)

    def test_copy_action_creates_palette_copy_record(self):
        """11. Copy action creates a PaletteCopy record."""
        self.client.login(username="user2", password="Password123!")
        url = reverse("community:copy", kwargs={"slug": self.public_palette.slug})
        self.client.post(url)
        self.assertTrue(PaletteCopy.objects.filter(source_palette=self.public_palette).exists())

    def test_export_permission_is_respected(self):
        """14. Export permission is respected."""
        # Test case: allow_export is True
        self.public_palette.allow_export = True
        self.public_palette.save()
        url = reverse("community:export_palette", kwargs={"slug": self.public_palette.slug, "export_format": "CSS"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment; filename=", response["Content-Disposition"])

        # Test case: allow_export is False
        self.public_palette.allow_export = False
        self.public_palette.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
