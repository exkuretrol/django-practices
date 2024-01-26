from django.urls import path
from .views import get_data, get_prods, ProdListView

urlpatterns = [
    path("goods/ajax_get_category/9x9shop", get_data, name="ajax_get_category"),
    path("goods/ajax_get_prods/9x9shop", get_prods, name="ajax_get_prods"),
    path(
        "ajax/", ProdListView.as_view(), name="ajax_test"
    ),
]
