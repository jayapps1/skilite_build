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

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


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
