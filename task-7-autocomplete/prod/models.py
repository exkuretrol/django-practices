from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Case, F, Value, When
from django.db.models.functions import Concat, Substr
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from manufacturer.models import Manufacturer


class CateTypeChoices(models.IntegerChoices):
    Cate = 1, _("大分類")
    SubCate = 2, _("中分類")
    SubSubCate = 3, _("小分類")


class ProdCategory(models.Model):

    cate_no = models.CharField(
        primary_key=True,
        verbose_name=_("分類編號"),
        max_length=6,
        validators=[
            RegexValidator(r"^\d{6}$", message=_("您必須輸入一個 6 位數的分類編號。"))
        ],
    )
    cate_name = models.CharField(verbose_name=_("分類名稱"), max_length=255)
    cate_type = models.PositiveSmallIntegerField(
        verbose_name=_("分類大小"),
        choices=CateTypeChoices,
        default=CateTypeChoices.Cate,
    )
    cate_cate_no = models.GeneratedField(
        verbose_name=_("分類大類編號"),
        expression=Case(
            When(cate_type=CateTypeChoices.Cate, then=F("cate_no")),
            When(
                cate_type=CateTypeChoices.SubCate,
                then=Concat(
                    Value("0000"),
                    Substr("cate_no", 3, 2),
                    output_field=models.CharField(max_length=6),
                ),
            ),
            default=Concat(
                Value("0000"),
                Substr("cate_no", 1, 2),
                output_field=models.CharField(max_length=6),
            ),
        ),
        output_field=models.CharField(max_length=6),
        db_persist=True,
        null=True,
    )

    cate_subcate_no = models.GeneratedField(
        verbose_name=_("分類中類編號"),
        expression=Case(
            When(
                cate_type=CateTypeChoices.SubSubCate,
                then=Concat(
                    Value("00"),
                    Substr("cate_no", 1, 4),
                    output_field=models.CharField(max_length=6),
                ),
            ),
            When(
                cate_type=CateTypeChoices.SubCate,
                then=F("cate_no"),
            ),
            default=None,
        ),
        output_field=models.CharField(max_length=6),
        db_persist=True,
        null=True,
    )

    cate_parent_no = models.GeneratedField(
        verbose_name=_("分類上層編號"),
        expression=Case(
            When(cate_type=CateTypeChoices.Cate, then=None),
            When(
                cate_type=CateTypeChoices.SubCate,
                then=Concat(
                    Value("0000"),
                    Substr("cate_no", 3, 2),
                    output_field=models.CharField(max_length=6),
                ),
            ),
            default=Concat(
                Value("00"),
                Substr("cate_no", 1, 4),
                output_field=models.CharField(max_length=6),
            ),
        ),
        output_field=models.CharField(max_length=6),
        db_persist=True,
        null=True,
    )

    def __str__(self) -> str:
        return self.cate_no + " - " + self.cate_name

    class Meta:
        ordering = ["cate_no"]


class SalesStatusChoices(models.IntegerChoices):
    NORMAL = 0, _("正常")
    ABNORMAL = 1, _("異常 (因為商品品質異常暫時停止銷售)")


class QualityAssuranceStatusChoices(models.IntegerChoices):
    NORMAL = 0, _("正常追蹤")
    NEW_PROD = 1, _("新產品追蹤")
    CASE = 2, _("案例追蹤")
    LICENSE = 3, _("證照追蹤")


class Prod(models.Model):
    prod_no = models.BigAutoField(primary_key=True, verbose_name=_("商品編號"))
    prod_name = models.CharField(verbose_name=_("商品名稱"), max_length=255)
    prod_desc = models.TextField(
        verbose_name=_("商品描述"), null=True, default=None, blank=True
    )
    prod_img = models.ImageField(
        upload_to="images/",
        verbose_name=_("商品圖片"),
        null=True,
        default=None,
        blank=True,
    )
    prod_quantity = models.PositiveIntegerField(default=0, verbose_name=_("商品數量"))

    prod_cate_no = models.ForeignKey(
        verbose_name=_("商品分類編號"),
        to=ProdCategory,
        on_delete=models.SET_NULL,
        null=True,
    )

    prod_effective_date = models.DateField(
        verbose_name=_("商品生效日期"),
        auto_now_add=True,
    )

    prod_sales_status = models.PositiveSmallIntegerField(
        verbose_name=_("商品銷售狀態"),
        choices=SalesStatusChoices,
        default=SalesStatusChoices.NORMAL,
    )

    prod_quality_assurance_status = models.PositiveSmallIntegerField(
        verbose_name=_("商品品保狀態"),
        choices=QualityAssuranceStatusChoices,
        default=QualityAssuranceStatusChoices.NORMAL,
    )

    prod_mfr_id = models.ForeignKey(
        verbose_name=_("商品廠商 ID"),
        to=Manufacturer,
        on_delete=models.CASCADE,
        default=1,
    )

    def __str__(self) -> str:
        return str(self.prod_no) + " - " + self.prod_name

    def get_absolute_url(self):
        return reverse("prod_detail", kwargs={"pk": self.prod_no})

    class Meta:
        ordering = ["prod_no"]
