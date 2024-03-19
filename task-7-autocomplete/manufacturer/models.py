from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import F
from django.db.models.functions import Concat


class Manufacturer(models.Model):
    mfr_id = models.BigAutoField(
        verbose_name="廠商 ID",
        primary_key=True,
    )
    mfr_main_id = models.CharField(
        verbose_name="廠商主要編號",
        max_length=8,
        validators=[
            RegexValidator(
                r"^\d{8}$",
                message="您必須輸入 8 位數的廠商主要編號。",
            )
        ],
    )
    mfr_sub_id = models.CharField(
        verbose_name="廠商次要編號",
        max_length=2,
        validators=[
            RegexValidator(
                r"^\d{2}$",
                message="您必須輸入 2 位數的廠商次要編號。",
            )
        ],
    )
    mfr_full_id = models.GeneratedField(
        expression=Concat(
            F("mfr_main_id"),
            F("mfr_sub_id"),
            output_field=models.CharField(max_length=10),
        ),
        output_field=models.CharField(max_length=10),
        verbose_name="廠商編號",
        max_length=10,
        unique=True,
        db_persist=True,
    )
    mfr_name = models.CharField(verbose_name="廠商名稱", max_length=255)
    mfr_address = models.CharField(verbose_name="廠商地址", max_length=255)
    mfr_created_at = models.DateTimeField(
        verbose_name="廠商建立時間", auto_now_add=True
    )
    mfr_updated_at = models.DateTimeField(
        verbose_name="廠商上次更新時間", auto_now=True
    )
    mfr_user_id = models.ForeignKey(
        verbose_name="廠商關聯的使用者",
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return self.mfr_name
