from django.urls import path

from .views import (
    ConfigView,
    CustomLoginView,
    ProfileView,
    SignUpView,
    UsernameAutocomplete,
)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    # autocomplete
    path(
        "username/autocomplele/",
        UsernameAutocomplete.as_view(),
        name="username_autocomplete",
    ),
    path("config/", ConfigView.as_view(), name="config"),
]
