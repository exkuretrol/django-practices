from typing import Any
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
)
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser


class CommonUserInfo(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "age",
        )

        labels = {
            "username": "Username",
            "email": "Email",
            "age": "Age",
        }


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields:
            widget = self.fields[field].widget
            print(widget.attrs)
            if widget.input_type in ["password", "email", "number", "text"]:
                widget.attrs.update({"class": "input-normal"})
    class Meta(CommonUserInfo.Meta):
        pass


class CustomUserAuthenticationForm(AuthenticationForm):
    def __init__(self, request: Any = ..., *args: Any, **kwargs: Any) -> None:
        super().__init__(request, *args, **kwargs)
        for field in self.fields:
            widget = self.fields[field].widget
            if widget.input_type in ["password", "text"]:
                widget.attrs.update({"class": "input-normal"})

    # username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True, "class": "input-normal"}))
    # password = forms.CharField(
    #     label=_("Password"),
    #     strip=False,
    #     widget=forms.PasswordInput(attrs={"class":"input-normal", "autocomplete": "current-password"}),
    # )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "age",
        )
