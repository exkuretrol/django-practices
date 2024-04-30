from django.urls import path

from .views import (
    ManufacturerAutocomplete,
    ManufacturerCurrentUserAutoComplete,
    ManufacturerUsernameAutoComplete,
)

urlpatterns = [
    path(
        "mfr/autocomplete/",
        ManufacturerAutocomplete.as_view(),
        name="mfr_autocomplete",
    ),
    path(
        "mfr/username/autocomplete/",
        ManufacturerUsernameAutoComplete.as_view(),
        name="mfr_username_autocomplete",
    ),
    path(
        "mfr/current_user/autocomplete/",
        ManufacturerCurrentUserAutoComplete.as_view(),
        name="mfr_current_user_autocomplete",
    ),
]
