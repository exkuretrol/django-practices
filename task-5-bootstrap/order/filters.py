import django_filters
from django.db import models

from .models import Order


class OrderFilter(django_filters.FilterSet):
    od_no = django_filters.BaseInFilter(
        label="訂單編號", lookup_expr="in", required=False
    )
    od_prod_no = django_filters.BaseInFilter(label="品號")
    od_prod_no__prod_name = django_filters.CharFilter(
        label="品名", lookup_expr="icontains"
    )
    od_mfr_id = django_filters.BaseInFilter(label="10碼廠編")
    od_mfr_id__mfr_name = django_filters.CharFilter(
        label="廠商名稱", lookup_expr="icontains"
    )
    od_mfr_id__mfr_user_id__username = django_filters.CharFilter(
        label="訂貨人員", lookup_expr="icontains"
    )
    od_date = django_filters.DateFromToRangeFilter(label="訂貨日期")
    od_except_arrival_date = django_filters.DateFromToRangeFilter(label="預期到貨日")

    class Meta:
        model = Order
        fields = [
            "od_no",
            "od_prod_no",
            "od_mfr_id",
            "od_date",
            "od_except_arrival_date",
        ]

        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {"lookup_expr": "icontains"},
            }
        }
