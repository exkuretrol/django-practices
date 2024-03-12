from django.contrib import admin
from order.models import Order, OrderProd


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "od_no",
        "od_mfr_id",
        "od_date",
        "od_except_arrival_date",
        "od_has_contact_form",
        "od_status",
        "od_warehouse_storage_fee_recipient",
    ]


class OrderProdAdmin(admin.ModelAdmin):
    list_display = [
        "op_id",
        "op_od_no",
        "op_prod_no",
        "op_quantity",
    ]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProd, OrderProdAdmin)
