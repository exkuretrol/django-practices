import django_filters
from django import forms

from .models import Order, OrderProd


def prod_filter(queryset, name, value):
    filtered_queryset = queryset
    for order in queryset:
        if order.orderprod_set.count() == 0:
            filtered_queryset = filtered_queryset.exclude(od_no=order.od_no)
            continue
        if name == "prod_name":
            for prod in order.orderprod_set.all():
                if value not in prod.op_prod_no.prod_name:
                    filtered_queryset = filtered_queryset.exclude(od_no=order.od_no)
                    break
        elif name == "prod_no":
            if order.orderprod_set.all().filter(op_prod_no__prod_no=value).count() == 0:
                filtered_queryset = filtered_queryset.exclude(od_no=order.od_no)

    return filtered_queryset


class OrderFilter(django_filters.FilterSet):
    od_no = django_filters.BaseInFilter(
        label="訂單編號", lookup_expr="in", required=False
    )

    od_prod_name = django_filters.CharFilter(
        field_name="prod_name", label="品名", method=prod_filter
    )
    od_prod_no = django_filters.NumberFilter(
        field_name="prod_no", label="品號", method=prod_filter
    )

    od_mfr_id__mfr_full_id = django_filters.CharFilter(
        label="10碼廠編", lookup_expr="exact"
    )
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
        fields = []


class OrderProdFilter(django_filters.FilterSet):
    op_od_no = django_filters.BaseInFilter(label="訂單編號")

    class Meta:
        model = OrderProd
        fields = []
