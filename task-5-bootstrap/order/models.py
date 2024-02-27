from django.db import models
from django.utils.translation import gettext_lazy as _
from manufacturer.models import Manufacturer
from prod.models import Prod


class StatusChoices(models.IntegerChoices):
    Generated = 0, _("訂單產生")
    Submitted = 1, _("訂單已傳檔")
    Closured = 2, _("訂單結案")
    Cancelled = 3, _("訂單取消")


class WarehouseStorageFeeRecipientChoices(models.IntegerChoices):
    NoCharge = 0, _("不收費")
    Manufacturer = 1, _("廠商")
    Customer = 2, _("客戶")


class Order(models.Model):
    od_no = models.BigIntegerField(primary_key=True, verbose_name="訂單編號")
    od_prod_no = models.ForeignKey(
        to=Prod, verbose_name=_("商品編號"), on_delete=models.SET_NULL, null=True
    )
    od_mfr_id = models.ForeignKey(
        to=Manufacturer, verbose_name=_("廠商 ID"), on_delete=models.SET_NULL, null=True
    )
    od_date = models.DateTimeField(verbose_name=_("訂單下訂日期"), auto_now_add=True)
    od_except_arrival_date = models.DateTimeField(verbose_name=_("預期到貨日期"))
    od_has_contact_form = models.BooleanField(verbose_name=_("有聯絡單"), default=False)
    od_contact_form_no = models.BigIntegerField(verbose_name=_("聯絡單編號"), default=0)
    od_status = models.PositiveSmallIntegerField(
        verbose_name=_("訂單狀態"),
        choices=StatusChoices,
        default=StatusChoices.Generated,
    )
    od_warehouse_storage_fee_recipient = models.PositiveSmallIntegerField(
        verbose_name=_("訂單寄倉費對象"),
        choices=WarehouseStorageFeeRecipientChoices,
        default=WarehouseStorageFeeRecipientChoices.NoCharge,
    )
    od_notes = models.TextField(verbose_name=_("訂單備註"), null=True)
