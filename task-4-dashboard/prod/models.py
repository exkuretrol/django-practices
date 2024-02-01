from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from manufacturer.models import Manufacturer


class CateTypeChoices(models.TextChoices):
    Cate = "J", _("Category")
    SubCate = "K", _("Sub Category")
    SubSubCate = "L", _("Sub Sub Category")


class ProdCategory(models.Model):
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

    def __str__(self) -> str:
        return self.cate_id + " - " + self.cate_name

    class Meta:
        ordering = ["cate_id"]


class SalesStatusChoices(models.IntegerChoices):
    NORMAL = 1, _("Normal")
    ABNORMAL = 0, _("Abnormal (Sales Suspended due to Quality Abnormality)")


class QualityAssuranceStatusChoices(models.IntegerChoices):
    NORMAL = 1, _("Normal Tracking")
    NEW_PROD = 2, _("New Product Tracking")
    CASE = 3, _("Case Tracking")
    LICENSE = 4, _("License Tracking")


class Prod(models.Model):
    prod_no = models.BigAutoField(primary_key=True, verbose_name="Product No.")
    prod_name = models.CharField(verbose_name="Product Name", max_length=255)
    prod_desc = models.TextField(verbose_name="Product Description", null=True)
    prod_img = models.ImageField(
        upload_to="images/", verbose_name="Product Img", null=True
    )
    prod_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Product Quantity"
    )

    prod_category = models.ForeignKey(
        to=ProdCategory, on_delete=models.SET_NULL, null=True
    )

    prod_effective_date = models.DateField(
        verbose_name="Product Effective Date",
        auto_now_add=True,
    )

    prod_sales_status = models.IntegerField(
        verbose_name="Product Sales Status",
        choices=SalesStatusChoices,
        default=SalesStatusChoices.NORMAL,
    )

    prod_quality_assurance_status = models.IntegerField(
        verbose_name="Product Quality Assurance Status",
        choices=QualityAssuranceStatusChoices,
        default=QualityAssuranceStatusChoices.NORMAL,
    )

    prod_mfr_id = models.ForeignKey(
        verbose_name="Manufacturer",
        to=Manufacturer,
        on_delete=models.CASCADE,
        default=1,
    )

    def __str__(self) -> str:
        return self.prod_name

    def get_absolute_url(self):
        return reverse("prod_list")

    class Meta:
        ordering = ["prod_no"]
