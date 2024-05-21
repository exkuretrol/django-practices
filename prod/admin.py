from django.contrib import admin

from .forms import ProdCommonInfo, ProdRestrictionCreateForm
from .models import Prod, ProdCategory, ProdRestriction


@admin.register(Prod)
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

    search_fields = ["prod_no", "prod_name"]

    list_display_links = ["prod_name"]


@admin.register(ProdCategory)
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


@admin.register(ProdRestriction)
class ProdRestrictionAdmin(admin.ModelAdmin):
    form = ProdRestrictionCreateForm
    list_display = [
        "pr_no",
        "pr_prod_no",
        "pr_unit_price",
        "pr_as_case_quantity",
        "pr_effective_start_date",
        "pr_effective_end_date",
    ]
    list_display_links = ["pr_no", "pr_prod_no"]
