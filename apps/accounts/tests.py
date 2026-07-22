from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
import pyotp
from apps.accounts.models import UserProfile, OTPCode

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


class AccountsSecurityAndMfaTests(TestCase):
    """
    Unit tests for Super Admin creation, Password Change enforcement, OTP recovery, and TOTP 2FA.
    """

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="superuser",
            password="SuperSecr3tPassword!",
            email="superuser@example.com",
        )
        self.user_phone = "+233244111222"
        self.regular_user = User.objects.create_user(
            username="regularuser",
            password="RegularPassword123!",
            email="regularuser@example.com",
            phone_number=self.user_phone,
        )

    def test_superuser_can_provision_staff_admin(self):
        """
        Verify that a superuser can create a Staff Admin with must_change_password=True.
        """
        self.client.login(username="superuser", password="SuperSecr3tPassword!")
        url = reverse("accounts:create_admin")
        
        # Post admin provisioning details
        response = self.client.post(
            url,
            {
                "username": "newstaff",
                "email": "newstaff@example.com",
                "phone_number": "+233244999999",
            },
        )
        self.assertRedirects(response, reverse("accounts:dashboard"))
        
        # Verify database record
        new_admin = User.objects.filter(username="newstaff").first()
        self.assertIsNotNone(new_admin)
        self.assertTrue(new_admin.is_staff)
        self.assertFalse(new_admin.is_superuser)
        self.assertTrue(new_admin.must_change_password)
        
        # Check minimal privileges group assignment
        self.assertTrue(new_admin.groups.filter(name="Staff Admins").exists())

    def test_must_change_password_middleware_redirection(self):
        """
        Verify that a user with must_change_password=True is forced to update their password.
        """
        # Create a user with must_change_password=True
        temp_admin = User.objects.create_user(
            username="tempadmin",
            password="DefaultPassword123!",
            email="tempadmin@example.com",
            must_change_password=True,
        )

        # Log in
        self.client.login(username="tempadmin", password="DefaultPassword123!")

        # Try to access dashboard
        response = self.client.get(reverse("accounts:dashboard"))
        # Middleware should redirect to change password view
        self.assertRedirects(response, reverse("accounts:change_password"))

        # Successfully change the password
        change_url = reverse("accounts:change_password")
        change_response = self.client.post(
            change_url,
            {
                "current_password": "DefaultPassword123!",
                "new_password": "NewSecr3tPassword2026!",
                "confirm_password": "NewSecr3tPassword2026!",
            },
        )
        self.assertRedirects(change_response, reverse("accounts:dashboard"))

        # Check model flag update
        temp_admin.refresh_from_db()
        self.assertFalse(temp_admin.must_change_password)

        # Dashboard should now load successfully (code 200)
        dashboard_response = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(dashboard_response.status_code, 200)

    def test_forgot_password_sends_otp_and_verifies_to_reset(self):
        """
        Verify the OTP-based password recovery flow.
        """
        # 1. Post to forgot password to request OTP
        forgot_url = reverse("accounts:forgot_password")
        response = self.client.post(forgot_url, {"phone_number": self.user_phone})
        self.assertRedirects(response, reverse("accounts:verify_otp"))

        # Check OTP record created
        otp_record = OTPCode.objects.filter(user=self.regular_user).first()
        self.assertIsNotNone(otp_record)
        self.assertEqual(len(otp_record.code), 6)

        # 2. Verify OTP digit inputs
        verify_url = reverse("accounts:verify_otp")
        verify_response = self.client.post(
            verify_url,
            {
                "digit1": otp_record.code[0],
                "digit2": otp_record.code[1],
                "digit3": otp_record.code[2],
                "digit4": otp_record.code[3],
                "digit5": otp_record.code[4],
                "digit6": otp_record.code[5],
            },
        )
        self.assertRedirects(verify_response, reverse("accounts:reset_password"))

        # 3. Post new password on reset screen
        reset_url = reverse("accounts:reset_password")
        reset_response = self.client.post(
            reset_url,
            {
                "new_password": "RecoveredPassword2026!",
                "confirm_password": "RecoveredPassword2026!",
            },
        )
        self.assertRedirects(reset_response, reverse("accounts:login"))

        # Verify password changed by logging in with the new password
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password("RecoveredPassword2026!"))

    def test_google_authenticator_2fa_login_interception(self):
        """
        Verify that enabling TOTP 2FA intercept logins with a 2FA challenge.
        """
        # Set TOTP secret and enable 2FA on regular user
        secret = pyotp.random_base32()
        self.regular_user.totp_secret = secret
        self.regular_user.totp_enabled = True
        self.regular_user.save()

        # Try to log in with standard credentials
        login_url = reverse("accounts:login")
        response = self.client.post(
            login_url,
            {"username": "regularuser", "password": "RegularPassword123!"},
        )
        
        # Should redirect to verify_2fa challenge instead of dashboard
        self.assertRedirects(response, reverse("accounts:verify_2fa"))
        
        # Verify user is not logged in yet in the active client session
        self.assertNotIn("_auth_user_id", self.client.session)

        # Generate a valid TOTP code
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        # Submit code to verify_2fa view
        verify_2fa_url = reverse("accounts:verify_2fa")
        verify_response = self.client.post(
            verify_2fa_url,
            {
                "digit1": valid_code[0],
                "digit2": valid_code[1],
                "digit3": valid_code[2],
                "digit4": valid_code[3],
                "digit5": valid_code[4],
                "digit6": valid_code[5],
            },
        )
        self.assertRedirects(verify_response, reverse("accounts:dashboard"))
        
        # Verify user is now fully authenticated
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.regular_user.id)
