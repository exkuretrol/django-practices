from django.contrib import admin
from order.models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "od_no",
        "od_prod_no",
        "od_mfr_id",
        "od_date",
        "od_except_arrival_date",
        "od_has_contact_form",
        "od_status",
        "od_warehouse_storage_fee_recipient",
    ]


admin.site.register(Order, OrderAdmin)
