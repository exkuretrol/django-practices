import django_filters

# from django.db.models import BaseManager
from django.utils.translation import gettext_lazy as _

from .models import Order, OrderProd


def prod_filter(queryset, name, value):
    if name == "prod_name":
        ops = OrderProd.objects.filter(op_prod_no__prod_name__icontains=value)
    if name == "prod_no":
        ops = OrderProd.objects.filter(op_prod_no=value)
    filtered_queryset = queryset.filter(orderprod_set__in=ops)

    return filtered_queryset


def prod_cate_filter(queryset, name, value):
    filtered_queryset = queryset
    for order in queryset:
        if order.orderprod_set.count() == 0:
            filtered_queryset = filtered_queryset.exclude(od_no=order.od_no)
            continue
        if name == "prod_cate":
            if (
                order.orderprod_set.all()
                .filter(op_prod_no__prod_cate_no__cate_cate_no=value.cate_no)
                .count()
                == 0
            ):
                filtered_queryset = filtered_queryset.exclude(od_no=order.od_no)
        elif name == "prod_subcate":
            if (
                order.orderprod_set.all()
                .filter(op_prod_no__prod_cate_no__cate_subcate_no=value.cate_no)
                .count()
                == 0
            ):
                filtered_queryset = filtered_queryset.exclude(od_no=order.od_no)
        elif name == "prod_subsubcate":
            if (
                order.orderprod_set.all()
                .filter(op_prod_no__prod_cate_no=value.cate_no)
                .count()
                == 0
            ):
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

    # od_prod_cate = django_filters.ModelChoiceFilter(
    #     field_name="prod_cate",
    #     label="大分類",
    #     method=prod_cate_filter,
    #     widget=autocomplete.ModelSelect2(
    #         url="prod_cate_autocomplete",
    #         attrs={
    #             "data-theme": "bootstrap-5",
    #             "data-placeholder": _("商品大分類編號或是分類名稱"),
    #         },
    #     ),
    #     queryset=ProdCategory.objects.all(),
    # )

    # od_prod_subcate = django_filters.ModelChoiceFilter(
    #     field_name="prod_subcate",
    #     label="中分類",
    #     method=prod_cate_filter,
    #     widget=autocomplete.ModelSelect2(
    #         url="prod_subcate_autocomplete",
    #         forward=["od_prod_cate"],
    #         attrs={
    #             "data-theme": "bootstrap-5",
    #             "data-placeholder": _("商品中分類編號或是分類名稱"),
    #         },
    #     ),
    #     queryset=ProdCategory.objects.all(),
    # )

    # od_prod_subsubcate = django_filters.ModelChoiceFilter(
    #     field_name="prod_subsubcate",
    #     label="小分類",
    #     method=prod_cate_filter,
    #     widget=autocomplete.ModelSelect2(
    #         url="prod_subsubcate_autocomplete",
    #         forward=["od_prod_subcate"],
    #         attrs={
    #             "data-theme": "bootstrap-5",
    #             "data-placeholder": _("商品小分類編號或是分類名稱"),
    #         },
    #     ),
    #     queryset=ProdCategory.objects.all(),
    # )

    class Meta:
        model = Order
        fields = []


class OrderRulesFilter(django_filters.FilterSet):
    pass
