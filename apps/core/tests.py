import time
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core import mail
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage

from apps.core.choices import EnquiryStatus, EnquiryType
from apps.core.models import ContactEnquiry
from apps.core.forms import ContactEnquiryForm

User = get_user_model()


class ContactEnquiryModelTest(TestCase):
    """
    Tests the ContactEnquiry model logic.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )

    def test_valid_enquiry_saves_correctly(self):
        enquiry = ContactEnquiry.objects.create(
            full_name="John Doe",
            email="john@example.com",
            phone="+123456789",
            subject="Question",
            message="This is a test message of 10+ characters.",
            enquiry_type=EnquiryType.GENERAL
        )
        self.assertIsNotNone(enquiry.pk)
        self.assertTrue(enquiry.enquiry_code.startswith("ENQ-"))
        self.assertEqual(enquiry.status, EnquiryStatus.NEW)
        self.assertFalse(enquiry.is_read)
        self.assertIsNone(enquiry.user)

    def test_enquiry_code_remains_unchanged_on_save(self):
        enquiry = ContactEnquiry.objects.create(
            full_name="John Doe",
            email="john@example.com",
            subject="Question",
            message="This is a test message of 10+ characters."
        )
        original_code = enquiry.enquiry_code
        enquiry.full_name = "Jane Doe"
        enquiry.save()
        self.assertEqual(enquiry.enquiry_code, original_code)

    def test_authenticated_enquiry_links_user(self):
        enquiry = ContactEnquiry.objects.create(
            user=self.user,
            full_name="Test User",
            email="testuser@example.com",
            subject="Support Request",
            message="This is a support message."
        )
        self.assertEqual(enquiry.user, self.user)

    def test_str_method_output(self):
        enquiry = ContactEnquiry.objects.create(
            full_name="John Doe",
            email="john@example.com",
            subject="Question",
            message="This is a test message of 10+ characters.",
            enquiry_type=EnquiryType.TECHNICAL_SUPPORT
        )
        expected = f"{enquiry.enquiry_code} - John Doe (TECHNICAL_SUPPORT)"
        self.assertEqual(str(enquiry), expected)

    def test_mark_as_read_method(self):
        enquiry = ContactEnquiry.objects.create(
            full_name="John Doe",
            email="john@example.com",
            subject="Question",
            message="This is a test message of 10+ characters."
        )
        self.assertFalse(enquiry.is_read)
        enquiry.mark_as_read()
        self.assertTrue(enquiry.is_read)

    def test_mark_resolved_method(self):
        enquiry = ContactEnquiry.objects.create(
            full_name="John Doe",
            email="john@example.com",
            subject="Question",
            message="This is a test message of 10+ characters."
        )
        self.assertEqual(enquiry.status, EnquiryStatus.NEW)
        self.assertIsNone(enquiry.responded_at)
        enquiry.mark_resolved()
        self.assertEqual(enquiry.status, EnquiryStatus.RESOLVED)
        self.assertIsNotNone(enquiry.responded_at)


class ContactEnquiryFormTest(TestCase):
    """
    Tests the ContactEnquiryForm validation and normalization rules.
    """

    def test_valid_form_data(self):
        form_data = {
            "full_name": "  John Doe  ",
            "email": "  JOHN@example.com  ",
            "phone": "  +123456  ",
            "enquiry_type": EnquiryType.TECHNICAL_SUPPORT,
            "subject": "  Need support  ",
            "message": "  This is a longer message that has more than 10 characters.  ",
            "website": "",  # Honeypot blank
        }
        form = ContactEnquiryForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test normalization on clean
        cleaned = form.cleaned_data
        self.assertEqual(cleaned["full_name"], "John Doe")
        self.assertEqual(cleaned["email"], "john@example.com")
        self.assertEqual(cleaned["phone"], "+123456")
        self.assertEqual(cleaned["subject"], "Need support")
        self.assertEqual(cleaned["message"], "This is a longer message that has more than 10 characters.")

    def test_honeypot_rejection(self):
        form_data = {
            "full_name": "John Doe",
            "email": "john@example.com",
            "enquiry_type": EnquiryType.GENERAL,
            "subject": "Support",
            "message": "Testing honeypot protection.",
            "website": "http://spambot.com",  # Honeypot filled
        }
        form = ContactEnquiryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("website", form.errors)
        self.assertEqual(form.errors["website"][0], "An error occurred. Please try again.")

    def test_invalid_email_rejected(self):
        form_data = {
            "full_name": "John Doe",
            "email": "not-an-email",
            "enquiry_type": EnquiryType.GENERAL,
            "subject": "Support",
            "message": "Testing invalid email support.",
        }
        form = ContactEnquiryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_short_message_rejected(self):
        form_data = {
            "full_name": "John Doe",
            "email": "john@example.com",
            "enquiry_type": EnquiryType.GENERAL,
            "subject": "Support",
            "message": "Too short",  # 9 chars
        }
        form = ContactEnquiryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)

    def test_phone_optional(self):
        form_data = {
            "full_name": "John Doe",
            "email": "john@example.com",
            "enquiry_type": EnquiryType.GENERAL,
            "subject": "Support",
            "message": "This is a message with 10+ characters.",
            "phone": "",  # Blank
        }
        form = ContactEnquiryForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["phone"], "")


class ContactViewTest(TestCase):
    """
    Tests the contact routing, view rendering, submissions, and cooldown limits.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        self.contact_url = reverse("core:contact")

    def test_contact_get_returns_200_and_uses_correct_template(self):
        response = self.client.get(self.contact_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/contact.html")

    def test_authenticated_initial_values_prefilled(self):
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(self.contact_url)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.initial.get("full_name"), "Test User")
        self.assertEqual(form.initial.get("email"), "testuser@example.com")

    def test_valid_anonymous_post_creates_enquiry_and_redirects(self):
        post_data = {
            "full_name": "Anon Visitor",
            "email": "anon@example.com",
            "phone": "+2335555555",
            "enquiry_type": EnquiryType.FEEDBACK,
            "subject": "Great Site",
            "message": "This platform is very helpful to our startup.",
            "website": "",
        }
        response = self.client.post(self.contact_url, post_data)
        self.assertEqual(ContactEnquiry.objects.count(), 1)
        enquiry = ContactEnquiry.objects.first()
        self.assertIsNone(enquiry.user)
        self.assertEqual(enquiry.full_name, "Anon Visitor")
        
        # Verify success redirect
        success_url = reverse("core:contact_success", kwargs={"enquiry_code": enquiry.enquiry_code})
        self.assertRedirects(response, success_url)

    def test_valid_authenticated_post_links_user(self):
        self.client.login(username="testuser", password="testpassword123")
        post_data = {
            "full_name": "Test User Override",
            "email": "testuser@example.com",
            "enquiry_type": EnquiryType.BUSINESS_ENQUIRY,
            "subject": "Business Partnership",
            "message": "Looking to integrate Skilite Build API in our platform.",
            "website": "",
        }
        response = self.client.post(self.contact_url, post_data)
        self.assertEqual(ContactEnquiry.objects.count(), 1)
        enquiry = ContactEnquiry.objects.first()
        self.assertEqual(enquiry.user, self.user)
        self.assertEqual(enquiry.full_name, "Test User Override")

    def test_invalid_post_creates_no_enquiry_and_re_renders(self):
        post_data = {
            "full_name": "",
            "email": "invalid-email",
            "message": "short",
        }
        response = self.client.post(self.contact_url, post_data)
        self.assertEqual(ContactEnquiry.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("full_name", form.errors)

    def test_duplicate_submission_cooldown(self):
        post_data = {
            "full_name": "Anon Visitor",
            "email": "anon@example.com",
            "enquiry_type": EnquiryType.GENERAL,
            "subject": "First submission",
            "message": "This is a valid enquiry message for testing.",
            "website": "",
        }
        # First submission succeeds
        response1 = self.client.post(self.contact_url, post_data)
        self.assertEqual(ContactEnquiry.objects.count(), 1)
        
        # Immediate second submission gets blocked by session cooldown
        response2 = self.client.post(self.contact_url, post_data)
        self.assertEqual(ContactEnquiry.objects.count(), 1)  # Still 1
        self.assertEqual(response2.status_code, 200)
        form = response2.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("__all__", form.errors)
        self.assertIn("Please wait", form.errors["__all__"][0])

    def test_email_notifications_sent(self):
        # Clear outbox
        mail.outbox.clear()
        post_data = {
            "full_name": "User Mail",
            "email": "usermail@example.com",
            "enquiry_type": EnquiryType.GENERAL,
            "subject": "Mail test",
            "message": "Testing the outbound django mail mock queue.",
            "website": "",
        }
        self.client.post(self.contact_url, post_data)
        # Should have sent 2 emails: 1 to staff, 1 to sender
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn("[Skilite Build Support]", mail.outbox[0].subject)
        self.assertIn("Skilite Build Enquiry Received", mail.outbox[1].subject)


class AboutViewTest(TestCase):
    """
    Tests the public about routing and template visual assertions.
    """

    def setUp(self):
        self.client = Client()
        self.about_url = reverse("core:about")

    def test_about_get_returns_200_and_uses_correct_template(self):
        response = self.client.get(self.about_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/about.html")
        
        # Verify content keywords are in HTML
        html = response.content.decode("utf-8")
        self.assertIn("About Skilite Build", html)
        self.assertIn("helping businesses build complete, usable website", html.lower())
        self.assertIn("colour systems", html.lower())
        self.assertIn("13 Semantic Roles", html)


class AdminRegistrationTest(TestCase):
    """
    Tests admin portal registration and actions security.
    """

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword123"
        )
        self.non_staff_user = User.objects.create_user(
            username="nonstaff",
            email="nonstaff@example.com",
            password="nonstaffpassword123"
        )
        self.enquiry = ContactEnquiry.objects.create(
            full_name="Submitter",
            email="submitter@example.com",
            subject="Issue",
            message="Please resolve this server error."
        )

    def test_admin_is_registered(self):
        self.assertIn(ContactEnquiry, admin.site._registry)
        model_admin = admin.site._registry[ContactEnquiry]
        self.assertIn("enquiry_code", model_admin.readonly_fields)
        self.assertIn("message", model_admin.readonly_fields)

    def test_non_staff_denied_admin_access(self):
        # Test anonymous access
        response = self.client.get("/admin/core/contactenquiry/")
        self.assertNotEqual(response.status_code, 200)

        # Test non-staff user access
        self.client.login(username="nonstaff", password="nonstaffpassword123")
        response = self.client.get("/admin/core/contactenquiry/")
        self.assertNotEqual(response.status_code, 200)

    def test_admin_actions_bulk_updates(self):
        # Login admin user
        self.client.login(username="adminuser", password="adminpassword123")
        
        # Get ModelAdmin instance
        model_admin = admin.site._registry[ContactEnquiry]
        queryset = ContactEnquiry.objects.filter(pk=self.enquiry.pk)
        
        # Setup dummy request
        request = self.factory.get("/admin/core/contactenquiry/")
        request.user = self.admin_user
        
        # Mock message_user to avoid message middleware setup requirements in unit tests
        model_admin.message_user = lambda req, msg, level=None, extra_tags=None: None
        
        # Action: Mark as read
        model_admin.mark_as_read_action(request, queryset)
        self.enquiry.refresh_from_db()
        self.assertTrue(self.enquiry.is_read)

        # Action: Mark resolved
        model_admin.mark_resolved_action(request, queryset)
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.status, EnquiryStatus.RESOLVED)
        self.assertIsNotNone(self.enquiry.responded_at)
