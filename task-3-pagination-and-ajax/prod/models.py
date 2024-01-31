from django.db import models
from django.utils.translation import gettext_lazy as _
from manufacturer.models import Manufacturer
from django.urls import reverse


class TypesInProd(models.TextChoices):
    TYPE1 = "T1", _("Human Readable Type 1")
    TYPE2 = "T2", _("Human Readable Type 2")
    TYPE3 = "T3", _("Human Readable Type 3")


class StatusInProd(models.TextChoices):
    ACTIVE = "AC", _("Active")
    INACTIVE = "IA", _("Inactive")


class Prod(models.Model):
    prod_no = models.BigAutoField(primary_key=True, verbose_name="Product No.")
    prod_name = models.CharField(verbose_name="Product Name", max_length=255)
    prod_desc = models.TextField(verbose_name="Product Desc")
    prod_type = models.CharField(
        verbose_name="Product Types",
        max_length=2,
        choices=TypesInProd,
        default=TypesInProd.TYPE1,
    )
    prod_img = models.ImageField(upload_to="images/", verbose_name="Product Img")
    prod_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Product Quantity"
    )
    prod_status = models.CharField(
        verbose_name="Product Status",
        max_length=2,
        choices=StatusInProd,
        default=StatusInProd.ACTIVE,
    )
    prod_mfr_id = models.ForeignKey(
        to=Manufacturer, on_delete=models.CASCADE, default=1
    )

    def __str__(self) -> str:
        return self.prod_name

    def get_absolute_url(self):
        return reverse("prod_list")

    class Meta:
        ordering = ["prod_no"]
