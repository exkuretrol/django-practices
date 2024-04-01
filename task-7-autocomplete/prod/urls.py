from django.urls import path
from django.views.generic.base import TemplateView

from .views import (
    CateAutocomplete,
    ProdAutocomplete,
    ProdCategoryAutocomplete,
    ProdCreateMultipleView,
    ProdCreateView,
    ProdDashboardView,
    ProdDeleteView,
    ProdDetailView,
    ProdListView,
    ProdUpdateMultipleView,
    ProdUpdateView,
    SubCateAutocomplete,
    SubSubCateAutocomplete,
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
        "prod_cate/all/autocomplete/",
        ProdCategoryAutocomplete.as_view(),
        name="prod_all_cate_autocomplete",
    ),
    path(
        "prod_cate/cate/autocomplete",
        CateAutocomplete.as_view(),
        name="prod_cate_autocomplete",
    ),
    path(
        "prod_cate/subcate/autocomplete",
        SubCateAutocomplete.as_view(),
        name="prod_subcate_autocomplete",
    ),
    path(
        "prod_cate/subsubcate/autocomplete",
        SubSubCateAutocomplete.as_view(),
        name="prod_subsubcate_autocomplete",
    ),
    path("prod/autocomplete/", ProdAutocomplete.as_view(), name="prod_autocomplete"),
]
