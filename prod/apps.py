from django.apps import AppConfig


class ProdConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "prod"
