from django.urls import path, reverse

from .views import OrderList

urlpatterns = [
    path(
        "order/",
        OrderList.as_view(),
        name="order_list",
    )
]
