from django.urls import path
from django.views.generic import TemplateView

from .views import (
    OrderCirculatedOrderView,
    OrderCreateMultipleView,
    OrderCreateView,
    OrderListView,
    OrderNoAutocomplete,
    OrderRulesView,
    OrderUpdateView,
)

urlpatterns = [
    path(
        "order/",
        OrderListView.as_view(),
        name="order_list",
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
    path(
        "order/rules/",
        OrderRulesView.as_view(),
        name="order_rules",
    ),
    path(
        "order/circulated_order/",
        OrderCirculatedOrderView.as_view(),
        name="order_circulated_order",
    ),
    # autocomplete
    path(
        "order/autocomplete/",
        OrderNoAutocomplete.as_view(),
        name="order_no_autocomplete",
    ),
]
