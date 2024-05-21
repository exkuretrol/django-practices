from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Case, F, Value, When
from django.db.models.functions import Concat, Substr
from django.urls import reverse
from django.utils import timezone
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
    ABNORMAL = 0, _("異常 (因為商品品質異常暫時停止銷售)")
    NORMAL = 1, _("正常")


class QualityAssuranceStatusChoices(models.IntegerChoices):
    NORMAL = 1, _("正常追蹤")
    NEW_PROD = 2, _("新產品追蹤")
    CASE = 3, _("案例追蹤")
    LICENSE = 4, _("證照追蹤")


class UnitChoices(models.IntegerChoices):
    INDIVIDUAL = 1, _("個")
    PIECE1 = 2, _("條")
    UNIT = 3, _("台")
    BOTTLE = 4, _("瓶")
    SET = 5, _("組")
    KIT = 6, _("套")
    PACK = 7, _("打")
    BAG1 = 8, _("包")
    BOX = 9, _("盒")
    CAN = 10, _("罐")
    BLOCK = 11, _("塊")
    ITEM = 12, _("件")
    SINGLE = 13, _("只")
    PORTION = 14, _("份")
    PIECE2 = 15, _("片")
    BUCKET = 16, _("桶")
    STICK = 17, _("支")
    CUP = 18, _("杯")
    PAIR = 19, _("雙")
    SHEET = 20, _("張")
    CARD = 21, _("卡")
    STRING = 22, _("串")
    BOOK = 23, _("本")
    ROLL1 = 24, _("捲")
    ROLL2 = 25, _("卷")
    CASE = 31, _("箱")
    BOWL = 55, _("碗")
    TOP = 60, _("頂")
    BAG2 = 61, _("袋")


class SellZoneChoices(models.TextChoices):
    COSMED_PHYSICAL = "1", _("康是美實體")
    COSMED_EC = "2", _("康是美EC")
    COSMED_PHYSICAL_EC = "3", _("康是美實體+EC")
    UNIKCY_PHYSICAL = "4", _("UNIKCY 實體")
    UNIKCY_EC = "5", _("UNIKCY EC")
    UNIKCY_PHYSICAL_EC = "6", _("UNIKCY 實體+EC")
    COSMED_PHYSICAL_UNIKCY_PHYSICAL = "7", _("康是美實體 / UNIKCY 實體")
    COSMED_PHYSICAL_UNIKCY_EC = "8", _("康是美實體 / UNIKCY EC")
    COSMED_PHYSICAL_UNIKCY_PHYSICAL_EC = "9", _("康是美實體 / UNIKCY 實體+EC")
    COSMED_EC_UNIKCY_PHYSICAL = "A", _("康是美EC / UNIKCY 實體")
    COSMED_EC_UNIKCY_EC = "B", _("康是美EC / UNIKCY EC")
    COSMED_EC_UNIKCY_PHYSICAL_EC = "C", _("康是美EC / UNIKCY 實體+EC")
    COSMED_PHYSICAL_EC_UNIKCY_PHYSICAL = "D", _("康是美實體+EC / UNIKCY 實體")
    COSMED_PHYSICAL_EC_UNIKCY_EC = "E", _("康是美實體+EC / UNIKCY EC")
    COSMED_PHYSICAL_EC_UNIKCY_PHYSICAL_EC = "F", _("康是美實體+EC / UNIKCY 實體+EC")


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
    prod_unit = models.PositiveSmallIntegerField(
        default=UnitChoices.INDIVIDUAL, choices=UnitChoices, verbose_name=_("商品單位")
    )

    prod_cate_no = models.ForeignKey(
        verbose_name=_("商品分類編號"),
        to=ProdCategory,
        on_delete=models.SET_NULL,
        null=True,
    )

    prod_effective_start_date = models.DateField(
        verbose_name=_("商品生效起日"),
        auto_now_add=True,
    )

    prod_effective_end_date = models.DateField(
        verbose_name=_("商品生效迄日"),
        default=timezone.make_aware(timezone.datetime(9999, 1, 1)),
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

    prod_cost_price = models.FloatField(verbose_name=_("商品成本價格"))

    prod_retail_price = models.FloatField(verbose_name=_("商品零售價格"))

    prod_sell_zone = models.CharField(max_length=1, verbose_name=_("商品銷售區域"))

    prod_outer_quantity = models.PositiveIntegerField(verbose_name=_("商品箱入數"))
    prod_inner_quantity = models.PositiveIntegerField(verbose_name=_("商品收縮數"))

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


class ProdRestriction(models.Model):
    pr_no = models.BigAutoField(primary_key=True, verbose_name=_("限制編號"))
    pr_prod_no = models.ForeignKey(
        verbose_name=_("商品限制編號"),
        to=Prod,
        on_delete=models.CASCADE,
    )
    pr_unit_price = models.PositiveBigIntegerField(
        verbose_name=_("商品限制單價"),
        default=0,
    )
    pr_as_case_quantity = models.PositiveIntegerField(
        verbose_name=_("商品限制成箱數"),
        default=0,
    )
    pr_effective_start_date = models.DateField(
        verbose_name=_("商品限制生效起日"), default=timezone.now
    )
    pr_effective_end_date = models.DateField(
        verbose_name=_("商品限制生效迄日"),
        default=timezone.make_aware(timezone.datetime(9999, 1, 1)),
    )
