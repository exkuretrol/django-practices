from django.contrib import admin

from .models import Prod, ProdCategory


class ProdAdmin(admin.ModelAdmin):
    list_display = [
        "prod_no",
        "prod_name",
        "prod_quantity",
        "prod_category",
        "prod_sales_status",
        "prod_quality_assurance_status",
        "prod_mfr_id",
    ]

    list_display_links = ["prod_name"]


class ProdCategoryAdmin(admin.ModelAdmin):
    list_display = [
        "cate_id",
        "cate_name",
        "parent_cate_id",
        "children_cate_id",
        "cate_type",
    ]
    list_display_links = ["cate_id"]


admin.site.register(Prod, ProdAdmin)
admin.site.register(ProdCategory, ProdCategoryAdmin)
