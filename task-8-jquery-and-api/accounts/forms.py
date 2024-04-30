from typing import Any

from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CommonUserInfo(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
        )

        labels = {
            "username": "使用者名稱",
            "email": "電子信箱",
        }


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "密碼"
        self.fields["password2"].label = "確認密碼"

    class Meta(CommonUserInfo.Meta):
        pass


class CustomUserAuthenticationForm(AuthenticationForm):
    def __init__(self, request: Any = ..., *args: Any, **kwargs: Any) -> None:
        super().__init__(request, *args, **kwargs)

        self.fields["username"].label = "使用者名稱"
        self.fields["password"].label = "密碼"

    error_messages = {
        "invalid_login": _(
            "請輸入正確的使用者名稱和密碼。請注意，兩個欄位可能區分大小寫。"
        ),
        "inactive": _("此帳戶未啟用。"),
    }

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
        )
