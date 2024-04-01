from django.contrib import admin
from order.models import Order, OrderProd, OrderRule

from .forms import OrderRuleCreateForm


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "od_no",
        "od_mfr_id",
        "od_date",
        "od_except_arrival_date",
        "od_has_contact_form",
        "od_warehouse_storage_fee_recipient",
    ]


@admin.register(OrderProd)
class OrderProdAdmin(admin.ModelAdmin):
    list_display = [
        "op_id",
        "op_od_no",
        "op_prod_no",
        "op_quantity",
        "op_status",
    ]


@admin.register(OrderRule)
class OrderRulesAdmin(admin.ModelAdmin):
    form = OrderRuleCreateForm
    list_display = [
        "or_id",
        "or_type",
        "or_prod_no",
        "or_mfr_id",
        "or_prod_cate_no",
        "or_cannot_order",
        "or_cannot_be_shipped_as_case",
        "or_order_amount",
        "or_order_quantity_cases",
        "or_effective_start_date",
        "or_effective_end_date",
    ]
