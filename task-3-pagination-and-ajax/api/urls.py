from django.urls import path
from .views import (
    create_prods,
)

urlpatterns = [
    path("goods/ajax_post_prods/9x9shop", create_prods, name="ajax_post_prods"),
]
