from django.urls import path
from .views import (
    ProdCreateMultipleView,
    create_prods,
)

urlpatterns = [
    path(
        "prods/create_multiple/",
        ProdCreateMultipleView.as_view(),
        name="prod_create_multiple",
    ),
    path("goods/ajax_post_prods/9x9shop", create_prods, name="ajax_post_prods"),
]
