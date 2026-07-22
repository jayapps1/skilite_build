from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


class BootstrapFormMixin:
    """
    Mixin to automatically add Bootstrap classes to form fields.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            widget_class = widget.attrs.get("class", "")

            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                new_class = f"{widget_class} form-select".strip()
            elif isinstance(widget, forms.CheckboxInput):
                new_class = f"{widget_class} form-check-input".strip()
            elif isinstance(widget, forms.FileInput):
                new_class = f"{widget_class} form-control".strip()
            else:
                new_class = f"{widget_class} form-control".strip()

            widget.attrs["class"] = new_class


class UserRegistrationForm(BootstrapFormMixin, UserCreationForm):
    """
    Form for registering a new user with a unique email.
    """

    email = forms.EmailField(
        required=True,
        help_text="Required. A valid email address is needed for notifications and password recovery.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class UserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    """
    Form to update core user account information.
    """

    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        required=False,
        help_text="Format: e.g. +233244123456. Required for SMS password recovery and 2FA.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "first_name", "last_name")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number", "").strip()
        if not phone_number:
            return None
        if User.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number


class UserProfileUpdateForm(BootstrapFormMixin, forms.ModelForm):
    """
    Form to update additional user profile preferences.
    """

    class Meta:
        model = UserProfile
        fields = (
            "display_name",
            "bio",
            "preferred_language",
            "preferred_theme",
            "company_name",
            "website_url",
            "profile_image",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us a bit about yourself..."}),
            "display_name": forms.TextInput(attrs={"placeholder": "e.g. Jane Doe"}),
            "company_name": forms.TextInput(attrs={"placeholder": "e.g. NovaTech Solutions"}),
            "website_url": forms.URLInput(attrs={"placeholder": "e.g. https://mybusiness.com"}),
        }


class AdminCreationForm(BootstrapFormMixin, forms.ModelForm):
    """
    Form used by super admins to provision new Staff Admins.
    """

    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        required=True,
        help_text="Required for SMS operations. Include country code e.g. +233244123456",
    )

    class Meta:
        model = User
        fields = ("username", "email", "phone_number")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()
        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone


class ForgotPasswordForm(BootstrapFormMixin, forms.Form):
    """
    Form to input phone number for password reset OTP.
    """

    phone_number = forms.CharField(
        required=True,
        label="Phone Number",
        widget=forms.TextInput(attrs={"placeholder": "e.g. +233244123456"}),
    )

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()
        if not User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("No user is registered with this phone number.")
        return phone


class ResetPasswordForm(BootstrapFormMixin, forms.Form):
    """
    Form to reset password after OTP verification.
    """

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter new password"}),
        label="New Password",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password"}),
        label="Confirm Password",
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class DashboardChangePasswordForm(BootstrapFormMixin, forms.Form):
    """
    Form to change password inside the user dashboard.
    """

    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Current password"}),
        label="Current Password",
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "New password"}),
        label="New Password",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password"}),
        label="Confirm Password",
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
