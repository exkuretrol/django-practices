from django.urls import path
from django.views.generic.base import TemplateView
from .views import (
    ProdListView,
    ProdCreateView,
    ProdDetailView,
    ProdDeleteView,
    ProdUpdateView,
    ProdCreateMultipleView,
    ProdUpdateMultipleView,
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
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
]
