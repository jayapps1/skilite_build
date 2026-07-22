from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management import call_command
from apps.palettes.models import Palette
from apps.palettes.services import PaletteLifecycleService
from apps.core.choices import ModerationStatus

User = get_user_model()

class RecycleBinTests(TestCase):
    """
    Tests for soft-deletion, restoration, permanent deletion, and auto-purge commands.
    """

    def setUp(self):
        self.username = "paletteowner"
        self.password = "P@ssword123!"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="owner@example.com"
        )
        self.palette = Palette.objects.create(
            name="My Redesign Palette",
            owner=self.user,
            is_active=True
        )

    def test_soft_delete_sets_deleted_at(self):
        """
        Verify that soft deleting a palette sets is_active=False and a deleted_at timestamp.
        """
        self.assertIsNone(self.palette.deleted_at)
        self.assertTrue(self.palette.is_active)

        # Execute soft delete
        PaletteLifecycleService.soft_delete(palette=self.palette)

        self.palette.refresh_from_db()
        self.assertFalse(self.palette.is_active)
        self.assertIsNotNone(self.palette.deleted_at)
        # Check that deleted_at is close to now
        self.assertLessEqual((timezone.now() - self.palette.deleted_at).total_seconds(), 5)

    def test_recycle_bin_view_returns_soft_deleted_palettes(self):
        """
        Verify that the RecycleBinView lists the user's recycled palettes.
        """
        self.client.login(username=self.username, password=self.password)
        
        # Soft delete the palette
        PaletteLifecycleService.soft_delete(palette=self.palette)

        url = reverse("palettes:recycle_bin")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "palettes/recycle_bin.html")
        self.assertIn(self.palette, response.context["palettes"])
        self.assertEqual(response.context["palettes"][0].days_remaining, 30)

    def test_restore_palette_restores_active_state(self):
        """
        Verify that restoring a recycled palette updates active states.
        """
        self.client.login(username=self.username, password=self.password)
        
        # Soft delete first
        PaletteLifecycleService.soft_delete(palette=self.palette)

        # Post to restore
        restore_url = reverse("palettes:restore", kwargs={"slug": self.palette.slug})
        response = self.client.post(restore_url)
        self.assertRedirects(response, reverse("palettes:my_palettes"))

        # Verify active states in DB
        self.palette.refresh_from_db()
        self.assertTrue(self.palette.is_active)
        self.assertIsNone(self.palette.deleted_at)
        self.assertEqual(self.palette.moderation_status, ModerationStatus.DRAFT)

    def test_permanent_delete_removes_from_database(self):
        """
        Verify that permanent deletion completely removes the record.
        """
        self.client.login(username=self.username, password=self.password)
        
        # Soft delete first
        PaletteLifecycleService.soft_delete(palette=self.palette)

        # Post to permanent delete
        delete_url = reverse("palettes:permanent_delete", kwargs={"slug": self.palette.slug})
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("palettes:recycle_bin"))

        # Record should no longer exist
        self.assertFalse(Palette.objects.filter(id=self.palette.id).exists())

    def test_clear_expired_palettes_management_command(self):
        """
        Verify that clear_expired_palettes command purges palettes older than 30 days.
        """
        # Create an expired recycled palette (manually set deleted_at to 31 days ago)
        expired_palette = Palette.objects.create(
            name="Expired Palette",
            owner=self.user,
            is_active=False,
            deleted_at=timezone.now() - timedelta(days=31)
        )

        # Create a fresh recycled palette (deleted_at set to 1 day ago)
        fresh_palette = Palette.objects.create(
            name="Fresh Recycled Palette",
            owner=self.user,
            is_active=False,
            deleted_at=timezone.now() - timedelta(days=1)
        )

        # Execute management command
        call_command("clear_expired_palettes")

        # Expired palette should be deleted
        self.assertFalse(Palette.objects.filter(id=expired_palette.id).exists())
        # Fresh palette should still exist
        self.assertTrue(Palette.objects.filter(id=fresh_palette.id).exists())
