from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
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


class ProdCategory(models.Model):
    class CateTypeChoices(models.TextChoices):
        Cate = "J", _("Category")
        SubCate = "K", _("Sub Category")
        SubSubCate = "L", _("Sub Sub Category")

    cate_id = models.CharField(
        verbose_name="Category ID",
        max_length=6,
        primary_key=True,
        validators=[
            RegexValidator(r"^\d{6}$", message="You MUST input a 6 digits category id.")
        ],
    )
    cate_name = models.CharField(verbose_name="Category Name", max_length=255)
    cate_type = models.CharField(
        verbose_name="Category Type",
        max_length=1,
        choices=CateTypeChoices,
        default=CateTypeChoices.Cate,
    )

    @property
    def parent_cate_id(self):
        "Return the parent category id of the given product."
        cate_id = self.cate_id[:4]
        return cate_id

    @property
    def children_cate_id(self):
        "Return the parent category id of the given product."
        return self.cate_id[-4:]
