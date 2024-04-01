from django.urls import path

from .views import ManufacturerAutocomplete, ManufacturerUsernameAutoComplete

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
]
