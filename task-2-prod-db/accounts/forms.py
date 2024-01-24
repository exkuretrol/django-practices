from typing import Any
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
)
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from .models import CustomUser
from django import forms


class CommonUserInfo(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "age",
        )

        widgets = {
            "username": forms.TextInput(attrs={"class": "input-normal"}),
            "email": forms.EmailInput(attrs={"class": "input-normal"}),
            "age": forms.NumberInput(attrs={"class": "input-normal"}),
        }

        labels = {
            "username": "Username",
            "email": "Email",
            "age": "Age",
        }


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "class": "input-normal"}
        ),
        help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "class": "input-normal"}
        ),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta(CommonUserInfo.Meta):
        pass


class CustomUserAuthenticationForm(AuthenticationForm):
    # def __init__(self, request: Any = ..., *args: Any, **kwargs: Any) -> None:
    #     super().__init__(request, *args, **kwargs)
    #     self.fields["username"].widget = forms.TextInput(attrs={"autofocus": True, "class": "input-normal"})

    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True, "class": "input-normal"}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class":"input-normal", "autocomplete": "current-password"}),
    )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "age",
        )
