from django.contrib import admin
from .models import Manufacturer

class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ["name", "location", "created_at", "updated_at", "user_id"]
    list_display = ["mfr_" + col for col in list_display]

admin.site.register(Manufacturer, ManufacturerAdmin)
