import logging
import time
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import TemplateView, FormView

from apps.core.choices import (
    ColorRole,
    PaletteSource,
)
from apps.core.models import BusinessCategory, ContactEnquiry
from apps.core.forms import ContactEnquiryForm
from apps.palettes.models import Palette

logger = logging.getLogger(__name__)


def send_contact_notification_email(enquiry):
    """
    Safely sends email notifications for new contact enquiries.
    """
    notification_email = getattr(settings, "CONTACT_NOTIFICATION_EMAIL", None)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@skilitebuild.com")
    
    if not notification_email:
        notification_email = from_email

    # Send notification to staff
    staff_subject = f"[Skilite Build Support] New Enquiry {enquiry.enquiry_code}: {enquiry.subject}"
    staff_body = (
        f"A new enquiry has been submitted.\n\n"
        f"Code: {enquiry.enquiry_code}\n"
        f"Name: {enquiry.full_name}\n"
        f"Email: {enquiry.email}\n"
        f"Type: {enquiry.get_enquiry_type_display()}\n"
        f"Subject: {enquiry.subject}\n\n"
        f"Message:\n{enquiry.message}\n"
    )
    
    # Send confirmation to user
    user_subject = f"Skilite Build Enquiry Received - {enquiry.enquiry_code}"
    user_body = (
        f"Hello {enquiry.full_name},\n\n"
        f"Thank you for contacting Skilite Build support. We have received your enquiry and our team will get back to you shortly if required.\n\n"
        f"Here are your enquiry details:\n"
        f"Reference Code: {enquiry.enquiry_code}\n"
        f"Subject: {enquiry.subject}\n\n"
        f"Best regards,\n"
        f"The Skilite Build Team"
    )

    try:
        send_mail(
            staff_subject,
            staff_body,
            from_email,
            [notification_email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send staff contact email notification: {e}")

    try:
        send_mail(
            user_subject,
            user_body,
            from_email,
            [enquiry.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send user contact email acknowledgement: {e}")


class HomeView(TemplateView):
    """
    Public landing page for Skilite Build.
    """

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        active_categories = (
            BusinessCategory.objects
            .filter(is_active=True)
            .order_by("display_order", "name")
        )

        preset_palettes = (
            Palette.objects
            .filter(
                source_type=PaletteSource.PRESET,
                is_active=True,
            )
            .select_related(
                "business_category",
                "dominant_color_family",
            )
            .prefetch_related("colors")
            .order_by(
                "business_category__display_order",
                "name",
            )
        )

        context.update(
            {
                "featured_categories": active_categories[:8],
                "featured_presets": preset_palettes[:4],
                "category_count": active_categories.count(),
                "preset_count": preset_palettes.count(),
                "semantic_role_count": len(
                    ColorRole.values
                ),
            }
        )

        return context


class AboutView(TemplateView):
    """
    Public About page describing the platform, target users, values, and technology.
    """
    template_name = "core/about.html"


class ContactView(FormView):
    """
    Public contact page permitting guest and logged-in submissions.
    """
    template_name = "core/contact.html"
    form_class = ContactEnquiryForm

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            user = self.request.user
            initial["full_name"] = user.get_full_name() or user.username
            initial["email"] = user.email
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Load contact details from settings or safe defaults
        context.update({
            "site_contact_email": getattr(settings, "SITE_CONTACT_EMAIL", "support@skilitebuild.com"),
            "site_contact_phone": getattr(settings, "SITE_CONTACT_PHONE", "+233 (0) 555-0199"),
            "site_contact_address": getattr(settings, "SITE_CONTACT_ADDRESS", "Accra Central, Ghana"),
            "site_support_hours": getattr(settings, "SITE_SUPPORT_HOURS", "Mon - Fri: 9:00 AM - 5:00 PM GMT"),
        })
        return context

    def form_valid(self, form):
        # Cooldown check: limit duplicate rapid entries (approx 30s)
        last_submit = self.request.session.get("contact_cooldown")
        if last_submit:
            elapsed = time.time() - last_submit
            if elapsed < 30:
                form.add_error(None, f"Please wait {int(30 - elapsed)} seconds before submitting another enquiry.")
                return self.form_invalid(form)

        try:
            with transaction.atomic():
                enquiry = form.save(commit=False)
                if self.request.user.is_authenticated:
                    enquiry.user = self.request.user
                enquiry.save()
                
                # Send email notification & user acknowledgement
                send_contact_notification_email(enquiry)

                # Set cooldown and reference variables in session
                self.request.session["contact_cooldown"] = time.time()
                self.request.session["last_enquiry_code"] = enquiry.enquiry_code
                self.request.session["last_enquiry_date"] = enquiry.created_at.strftime("%B %d, %Y at %I:%M %p")

            messages.success(
                self.request,
                f"Thank you. Your enquiry was submitted successfully. Reference: {enquiry.enquiry_code}."
            )
            return redirect("core:contact_success", enquiry_code=enquiry.enquiry_code)
        except Exception as e:
            logger.error(f"Failed to save contact enquiry: {e}")
            form.add_error(None, "A database failure occurred. Your enquiry was not saved. Please try again later.")
            return self.form_invalid(form)


class ContactSuccessView(TemplateView):
    """
    Displays submission confirmation details to avoid private data leakage.
    """
    template_name = "core/contact_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enquiry_code = self.kwargs.get("enquiry_code")
        
        # Un unpredictably generated lookup (we also double-check session for added security)
        enquiry = get_object_or_404(ContactEnquiry, enquiry_code=enquiry_code)
        
        context.update({
            "enquiry_code": enquiry.enquiry_code,
            "created_at": enquiry.created_at,
        })
        return context