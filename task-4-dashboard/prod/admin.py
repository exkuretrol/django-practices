from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Prod, ProdCategory


class ProdAdmin(admin.ModelAdmin):
    list_display = [
        "prod_no",
        "prod_name",
        "prod_desc",
        "prod_type",
        "prod_status",
        "prod_quantity",
        "prod_mfr_id",
    ]


class ProdCategoryAdmin(admin.ModelAdmin):
    list_display = [
        "cate_id",
        "cate_name",
        "parent_cate_id",
        "children_cate_id",
        "cate_type",
    ]
    list_display_links = ["cate_id"]
    # def parent_cate_id(self, obj):
    #     app_label = obj._meta.app_label
    #     model_label = obj._meta.model_name
    #     if obj.parent_cate_id is None: return mark_safe("-")
    #     url = reverse(
    #         f'admin:{app_label}_{model_label}_change', args=(obj.parent_cate_id,)
    #     )
    #     return mark_safe(f'<a href="{url}">{obj.parent_cate_id}</a>')


admin.site.register(Prod, ProdAdmin)
admin.site.register(ProdCategory, ProdCategoryAdmin)
