from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from apps.core.models import ContactEnquiry
from apps.core.choices import EnquiryType


class ContactEnquiryForm(forms.ModelForm):
    """
    Public form to submit contact enquiries.
    """
    # Honeypot field (must remain empty for real submissions)
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="Leave blank if human",
        help_text="Spam protection"
    )

    class Meta:
        model = ContactEnquiry
        fields = [
            "full_name",
            "email",
            "phone",
            "enquiry_type",
            "subject",
            "message",
        ]
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your full name",
                    "autocomplete": "name",
                    "required": "required",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your email address",
                    "autocomplete": "email",
                    "required": "required",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your phone number (optional)",
                    "autocomplete": "tel",
                }
            ),
            "enquiry_type": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": "required",
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Subject of your enquiry",
                    "required": "required",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "How can we help you? (Minimum 10 characters)",
                    "rows": 6,
                    "required": "required",
                }
            ),
        }

    def clean_website(self):
        website = self.cleaned_data.get("website", "").strip()
        if website:
            raise ValidationError("An error occurred. Please try again.")
        return website

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name", "").strip()
        if not full_name:
            raise ValidationError("Full name is required and cannot be empty.")
        return full_name

    def clean_subject(self):
        subject = self.cleaned_data.get("subject", "").strip()
        if not subject:
            raise ValidationError("Subject is required and cannot be empty.")
        return subject

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise ValidationError("Email address is required.")
        # Apply standard Django email validator
        EmailValidator()(email)
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        return phone

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if not message:
            raise ValidationError("Message is required and cannot be empty.")
        if len(message) < 10:
            raise ValidationError("Message must be at least 10 characters long.")
        if len(message) > 5000:
            raise ValidationError("Message cannot exceed 5000 characters.")
        return message
