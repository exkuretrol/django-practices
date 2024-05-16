from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from manufacturer.models import Manufacturer
from prod.models import Prod, ProdCategory


class WarehouseStorageFeeRecipientChoices(models.IntegerChoices):
    NoCharge = 0, _("不收費")
    Manufacturer = 1, _("廠商")
    Customer = 2, _("客戶")


class Order(models.Model):
    od_no = models.BigIntegerField(primary_key=True, verbose_name="訂單編號")
    od_mfr_id = models.ForeignKey(
        to=Manufacturer,
        verbose_name=_("訂單廠商 ID"),
        on_delete=models.SET_NULL,
        null=True,
    )
    od_date = models.DateTimeField(verbose_name=_("訂單下訂日期"), default=timezone.now)
    od_except_arrival_date = models.DateField(verbose_name=_("定單預期到貨日期"))
    od_has_contact_form = models.BooleanField(
        verbose_name=_("訂單有聯絡單"), default=False
    )
    od_contact_form_no = models.BigIntegerField(
        verbose_name=_("訂單聯絡單編號"), default=None, null=True, blank=True
    )
    od_warehouse_storage_fee_recipient = models.PositiveSmallIntegerField(
        verbose_name=_("訂單寄倉費對象"),
        choices=WarehouseStorageFeeRecipientChoices,
        default=WarehouseStorageFeeRecipientChoices.NoCharge,
    )
    # TODO: add order source field
    od_notes = models.TextField(verbose_name=_("訂單備註"), null=True, blank=True)
    od_contact_form_notes = models.TextField(
        verbose_name=_("聯絡單備註"), null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["od_no", "od_date"], name="unique_order")
        ]

    def __str__(self):
        return f"{self.od_no}"


class StatusChoices(models.IntegerChoices):
    Generated = 0, _("訂單產生")
    Submitted = 1, _("訂單已傳檔")
    Closured = 2, _("訂單結案")
    Cancelled = 3, _("訂單取消")


class OrderProd(models.Model):
    op_id = models.BigAutoField(primary_key=True, verbose_name="訂單商品 ID")
    op_od_no = models.ForeignKey(
        to=Order,
        verbose_name="訂單編號",
        on_delete=models.CASCADE,
        related_name="orderprod_set",
    )
    op_status = models.PositiveSmallIntegerField(
        verbose_name=_("訂單狀態"),
        choices=StatusChoices,
        default=StatusChoices.Generated,
    )
    op_prod_no = models.ForeignKey(
        to=Prod, verbose_name="訂單商品編號", on_delete=models.SET_NULL, null=True
    )
    op_quantity = models.PositiveBigIntegerField(verbose_name="訂單商品數量", default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["op_od_no", "op_prod_no"], name="unique_order_prod"
            )
        ]


class OrderRuleTypeChoices(models.IntegerChoices):
    Product = 0, _("商品")
    Manufacturer = 1, _("廠商")
    ProductCategory = 2, _("商品類別")


class OrderRule(models.Model):
    or_id = models.BigAutoField(primary_key=True, verbose_name=_("訂單規則 ID"))
    or_type = models.PositiveSmallIntegerField(
        verbose_name=_("訂單規則類別"),
        choices=OrderRuleTypeChoices,
        default=OrderRuleTypeChoices.Product,
    )
    or_prod_no = models.ForeignKey(
        to=Prod,
        verbose_name=_("訂單規則商品編號"),
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
    )
    or_mfr_id = models.ForeignKey(
        to=Manufacturer,
        verbose_name=_("訂單規則廠商 ID"),
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
    )
    or_prod_cate_no = models.ForeignKey(
        to=ProdCategory,
        verbose_name=_("訂單規則商品分類編號"),
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True,
    )
    or_cannot_order = models.BooleanField(
        verbose_name=_("訂單規則不可訂貨"), default=False
    )
    or_shipped_as_case = models.BooleanField(
        verbose_name=_("訂單規則須成箱"), default=False
    )
    or_order_price = models.PositiveBigIntegerField(
        verbose_name=_("訂單規則訂貨金額"), null=True, blank=True, default=None
    )
    or_order_cases_quantity = models.PositiveBigIntegerField(
        verbose_name=_("訂單規則訂貨箱數"), null=True, blank=True, default=None
    )
    or_notes = models.TextField(
        verbose_name=_("訂單規則備註"), null=True, blank=True, default=None
    )
    or_effective_start_date = models.DateField(
        verbose_name=_("訂單規則生效起日"), default=timezone.now
    )
    or_effective_end_date = models.DateField(
        verbose_name=_("訂單規則生效迄日"),
        default=timezone.make_aware(timezone.datetime(9999, 1, 1)),
    )

    def __str__(self):
        attrs = []
        attrs.append(f"type: {OrderRuleTypeChoices(self.or_type).label}")
        if self.or_type == OrderRuleTypeChoices.Product:
            attrs.append(f"obj: {self.or_prod_no}")
        elif self.or_type == OrderRuleTypeChoices.Manufacturer:
            attrs.append(f"obj: {self.or_mfr_id}")
        else:
            attrs.append(f"obj: {self.or_prod_cate_no}")

        if self.or_cannot_order:
            attrs.append("orderable: False")
        if self.or_shipped_as_case:
            attrs.append("as_case: True")
        if self.or_order_price:
            attrs.append(f"order_price: {self.or_order_price}")
        if self.or_order_cases_quantity:
            attrs.append(f"order_cases: {self.or_order_cases_quantity}")
        if self.or_notes:
            attrs.append(f"notes: {self.or_notes}")

        return f"rule ({self.pk}) {", ".join(attrs)}"
