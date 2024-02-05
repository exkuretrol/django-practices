from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Manufacturer(models.Model):
    mfr_id = models.CharField(
        primary_key=True,
        max_length=10,
        validators=[
            RegexValidator(
                r"^\d{8}$|^\d{10}$",
                message="You MUST input an 8 or 10 digits category id.",
            )
        ],
    )
    mfr_name = models.CharField(max_length=255)
    mfr_location = models.CharField(max_length=255)
    mfr_created_at = models.DateTimeField(auto_now_add=True)
    mfr_updated_at = models.DateTimeField(auto_now=True)
    mfr_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.mfr_name
