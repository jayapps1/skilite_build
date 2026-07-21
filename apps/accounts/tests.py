from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import UserProfile

User = get_user_model()


class AccountsAuthTests(TestCase):
    """
    Unit tests for User authentication, signals, views, and forms.
    """

    def setUp(self):
        self.username = "testuser"
        self.password = "Secr3tP@ss123"
        self.email = "testuser@example.com"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email,
        )

    def test_profile_creation_signal(self):
        """
        Verify that a UserProfile is created automatically when a User is created.
        """
        # User profile should have been created in setUp
        profile = UserProfile.objects.filter(user=self.user).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)

    def test_login_view_loads(self):
        """
        Verify that the login page loads with code 200.
        """
        url = reverse("accounts:login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_register_view_loads(self):
        """
        Verify that the registration page loads with code 200.
        """
        url = reverse("accounts:register")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_dashboard_redirects_unauthenticated(self):
        """
        Verify that the dashboard redirects anonymous users to login.
        """
        url = reverse("accounts:dashboard")
        response = self.client.get(url)
        login_url = reverse("accounts:login")
        self.assertRedirects(response, f"{login_url}?next={url}")

    def test_dashboard_loads_authenticated(self):
        """
        Verify that the dashboard loads for authenticated users.
        """
        self.client.login(username=self.username, password=self.password)
        url = reverse("accounts:dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/dashboard.html")

    def test_profile_loads_authenticated(self):
        """
        Verify that the user profile page loads for authenticated users.
        """
        self.client.login(username=self.username, password=self.password)
        url = reverse("accounts:profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_settings_loads_authenticated(self):
        """
        Verify that settings load and render forms.
        """
        self.client.login(username=self.username, password=self.password)
        url = reverse("accounts:settings")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/settings.html")
        self.assertIn("user_form", response.context)
        self.assertIn("profile_form", response.context)


from apps.accounts.models import UserActivityLog, log_user_activity


class UserActivityLogTests(TestCase):
    """
    Tests for UserActivityLog auditing.
    """

    def setUp(self):
        self.username = "audituser"
        self.password = "Secr3tP@ss123!"
        self.email = "audituser@example.com"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email,
        )

    def test_log_user_activity_utility(self):
        """
        Verify that log_user_activity creates an activity record.
        """
        log = log_user_activity(None, self.user, "Custom Action", "Some custom details")
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, "Custom Action")
        self.assertEqual(log.details, "Some custom details")
        self.assertEqual(UserActivityLog.objects.filter(user=self.user).count(), 1)

    def test_login_creates_activity_log(self):
        """
        Verify that a successful login creates a UserActivityLog entry.
        """
        self.client.post(
            reverse("accounts:login"),
            {"username": self.username, "password": self.password},
        )
        logs = UserActivityLog.objects.filter(user=self.user, action="Logged In")
        self.assertTrue(logs.exists())
