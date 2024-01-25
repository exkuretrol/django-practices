from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Prod(models.Model):
    class TypesInProd(models.TextChoices):
        TYPE1 = "T1", _("Human Readable Type 1")
        TYPE2 = "T2", _("Human Readable Type 2")
        TYPE3 = "T3", _("Human Readable Type 3")

    class StatusInProd(models.TextChoices):
        ACTIVE = "AC", _("Active")
        INACTIVE = "IA", _("Inactive")

    prod_no = models.BigAutoField(primary_key=True)
    prod_name = models.CharField(max_length=255)
    prod_desc = models.TextField()
    prod_type = models.CharField(
        max_length=2,
        choices=TypesInProd,
        default=TypesInProd.TYPE1,
    )
    prod_img = models.ImageField(upload_to="images/")
    prod_quantity = models.PositiveIntegerField(default=0)
    prod_status = models.CharField(
        max_length=2,
        choices=StatusInProd,
        default=StatusInProd.ACTIVE,
    )

    def __str__(self) -> str:
        return self.prod_name

    def get_absolute_url(self):
        return reverse("prod_list")
