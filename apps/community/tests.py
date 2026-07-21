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
