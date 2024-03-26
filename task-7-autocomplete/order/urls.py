from django.urls import path
from django.views.generic import FormView, TemplateView

from .forms import TestLinkedAutoCompleteForm
from .views import (
    OrderBeforeCreateView,
    OrderCreateMultipleView,
    OrderCreateView,
    OrderListView,
    OrderRulesView,
    OrderUpdateView,
)


class TestLinkedAutoCompleteView(FormView):
    form_class = TestLinkedAutoCompleteForm
    template_name = "order_test_linked_autocomplete.html"


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
    path(
        "order/test_linked_autocomplete/",
        TestLinkedAutoCompleteView.as_view(),
        name="test_linked_autocomplete",
    ),
    path("order/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path(
        "order/rules/",
        OrderRulesView.as_view(),
        name="order_rules",
    ),
]
