from django.contrib import admin
from .models import Prod


class ProdAdmin(admin.ModelAdmin):
    list_display = [
        "prod_no",
        "prod_name",
        "prod_desc",
        "prod_type",
        "prod_status",
        "prod_quantity",
    ]


admin.site.register(Prod, ProdAdmin)
