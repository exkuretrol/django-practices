from django.urls import path
from django.views.generic import TemplateView

from .views import (
    OrderBeforeCreateView,
    OrderCreateMultipleView,
    OrderCreateView,
    OrderListView,
    OrderUpdateView,
)

urlpatterns = [
    path(
        "order/",
        OrderListView.as_view(),
        name="order_list",
    ),
    path(
        "order/create_clipboard/",
        OrderBeforeCreateView.as_view(),
        name="order_create_clipboard",
    ),
    path(
        "order/create/",
        OrderCreateView.as_view(),
        name="order_create",
    ),
    path(
        "order/create_multiple/",
        OrderCreateMultipleView.as_view(),
        name="order_create_multiple",
    ),
    path("order/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
]
