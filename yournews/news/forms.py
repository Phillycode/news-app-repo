"""Django forms for the YourNews application.

This module contains all form definitions for user authentication,
content creation, role management, and admin functions.
"""

from django import forms
from .models import RoleApplication, Article, Newsletter, Publisher
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

CustomUser = get_user_model()


class RegisterForm(UserCreationForm):
    """User registration form.

    Extends Django's UserCreationForm to register new users with
    username, email, and password validation. All users start with
    'reader' role.
    """

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]


class LoginForm(AuthenticationForm):
    """User login form.

    Extends Django's AuthenticationForm for user authentication with
    username and password fields.
    """

    class Meta:
        model = CustomUser
        fields = ["username", "password"]


class RoleApplicationForm(forms.ModelForm):
    """Form for users to apply for role changes.

    Allows readers to apply for journalist, editor, or publisher roles.
    Includes role selection and motivation text area with
    placeholder text.
    """

    class Meta:
        model = RoleApplication
        fields = ["applied_role", "motivation"]
        widgets = {
            "motivation": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Explain why you should be approved for this role..."
                    ),
                }
            )
        }


class RoleApplicationAdminForm(forms.ModelForm):
    """Admin form for processing role applications.

    Extended form used by admins to approve/reject role applications.
    Includes publisher selection field for assigning journalists and
    editors to specific publishers.
    """

    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        help_text="Select a publisher if approving a journalist or editor.",
    )

    class Meta:
        model = RoleApplication
        fields = "__all__"


class ForgotPasswordForm(forms.Form):
    """Form for password reset requests.

    Simple form with email field for users to request password reset.
    Validates email format and triggers reset email if user exists.
    """

    email = forms.EmailField(
        label="Enter your email",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )


class ResetPasswordForm(forms.Form):
    """Form for setting new password during reset process.

    Validates new password strength and confirms password match.
    Used in conjunction with secure reset tokens.
    """

    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        validators=[validate_password],
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean(self):
        """Validate that both password fields match.

        Returns:
            dict: Cleaned form data if validation passes.

        Raises:
            ValidationError: If passwords don't match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class ArticleForm(forms.ModelForm):
    """Form for creating and editing articles.

    Used by journalists to create articles that require editor approval.
    Includes title and content fields with Bootstrap styling.
    """

    class Meta:
        model = Article
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 6}
            ),
        }


class NewsletterForm(forms.ModelForm):
    """Form for creating and editing newsletters.

    Used by journalists to create newsletters that are published
    immediately without editor approval. Includes title and content
    fields with larger text area for newsletter content.
    """

    class Meta:
        model = Newsletter
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 8}
            ),
        }
