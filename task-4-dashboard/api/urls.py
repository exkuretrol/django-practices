from django.urls import path
from .views import (
    create_prods,
    update_prods,
)

urlpatterns = [
    path("goods/ajax_create_prods/9x9shop", create_prods, name="ajax_create_prods"),
    path("goods/ajax_update_prods/9x9shop", update_prods, name="ajax_update_prods"),
]
