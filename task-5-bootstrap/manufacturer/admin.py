from django.contrib import admin

from .models import Manufacturer


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "main_id",
        "sub_id",
        "name",
        "location",
        "created_at",
        "updated_at",
        "user_id",
    ]
    list_display = ["mfr_" + col for col in list_display]
    sortable_by = ["mfr_id", "mfr_main_id"]


admin.site.register(Manufacturer, ManufacturerAdmin)
