from django.contrib import admin

from .models import Manufacturer


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = [
        "mfr_id",
        "mfr_full_id",
        "mfr_name",
        "mfr_address",
        "mfr_created_at",
        "mfr_updated_at",
        "mfr_user_id",
    ]
    sortable_by = ["mfr_main_id", "mfr_sub_id"]


admin.site.register(Manufacturer, ManufacturerAdmin)
