from django.urls import path
from django.views.generic.base import TemplateView

from .views import (
    ManufacturerAutocomplete,
    ProdCategoryAutocomplete,
    ProdCreateMultipleView,
    ProdCreateView,
    ProdDashboardView,
    ProdDeleteView,
    ProdDetailView,
    ProdListView,
    ProdUpdateMultipleView,
    ProdUpdateView,
)

urlpatterns = [
    path("prods/", ProdListView.as_view(), name="prod_list"),
    path("prods/create/", ProdCreateView.as_view(), name="prod_create"),
    path("prods/<int:pk>/", ProdDetailView.as_view(), name="prod_detail"),
    path("prods/<int:pk>/update/", ProdUpdateView.as_view(), name="prod_update"),
    path("prods/<int:pk>/delete/", ProdDeleteView.as_view(), name="prod_delete"),
    # with ajax
    path(
        "prods/create_multiple/",
        ProdCreateMultipleView.as_view(),
        name="prod_create_multiple",
    ),
    path(
        "prods/update_multiple/",
        ProdUpdateMultipleView.as_view(),
        name="prod_update_multiple",
    ),
    # d3.js
    path(
        "prods/dashboard/",
        ProdDashboardView.as_view(),
        name="prod_dashboard",
    ),
    # autocomplete
    path(
        "prods/autocomplete/",
        ProdCategoryAutocomplete.as_view(),
        name="prod_autocomplete",
    ),
    path(
        "mfrs/autocomplete/",
        ManufacturerAutocomplete.as_view(),
        name="manufacturer_autocomplete",
    ),
]
