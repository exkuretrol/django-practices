from django.urls import path

from .views import OrderListView, OrderUpdateView

urlpatterns = [
    path(
        "order/",
        OrderListView.as_view(),
        name="order_list",
    ),
    path("order/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
]
