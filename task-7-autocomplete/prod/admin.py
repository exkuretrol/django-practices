from django.contrib import admin

from .forms import ProdCommonInfo
from .models import Prod, ProdCategory


class ProdAdmin(admin.ModelAdmin):
    form = ProdCommonInfo
    list_display = [
        "prod_no",
        "prod_name",
        "prod_quantity",
        "prod_cate_no",
        "prod_sales_status",
        "prod_quality_assurance_status",
        "prod_mfr_id",
    ]

    list_display_links = ["prod_name"]


class ProdCategoryAdmin(admin.ModelAdmin):
    list_display = [
        "cate_no",
        "cate_name",
        "cate_type",
        "cate_parent_no",
        "cate_cate_no",
        "cate_subcate_no",
    ]
    list_display_links = ["cate_no"]


admin.site.register(Prod, ProdAdmin)
admin.site.register(ProdCategory, ProdCategoryAdmin)
