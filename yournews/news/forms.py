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
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]


class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "password"]


class RoleApplicationForm(forms.ModelForm):
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
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        help_text="Select a publisher if approving a journalist or editor.",
    )

    class Meta:
        model = RoleApplication
        fields = "__all__"


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Enter your email",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )


class ResetPasswordForm(forms.Form):
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
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")

        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class ArticleForm(forms.ModelForm):
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
    class Meta:
        model = Newsletter
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 8}
            ),
        }
