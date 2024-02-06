import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Prod


class ImageColumn(tables.Column):
    def render(self, value):
        return format_html(f"<img src='{value.url}' width='100' height=auto />")


class DescColumn(tables.Column):
    def render(self, value):
        return f"{value[:20]}..."


class ProdTable(tables.Table):
    prod_img = ImageColumn()
    prod_desc = DescColumn()

    class Meta:
        model = Prod
        row_attrs = {"data-id": lambda record: record.pk}


def get_user_id(**kwargs):
    records = kwargs.get("record", None)
    if records is None:
        return 0
    user_id = records.get("user_id", None)
    if user_id is None:
        return 0
    else:
        return user_id


class ProdMfrTable(tables.Table):
    user_name = tables.Column(
        verbose_name="User", attrs={"td": {"user-id": get_user_id}}
    )
    prod_nums = tables.Column(verbose_name="Product Numbers")
    mfr_main_nums = tables.Column(verbose_name="Main Manufacturer Numbers")
    mfr_sub_nums = tables.Column(verbose_name="Sub Manufacturer Numbers")


class ProdMfrTable(tables.Table):
    user_name = tables.Column(
        verbose_name="User", attrs={"td": {"user-id": get_user_id}}
    )
    prod_nums = tables.Column(verbose_name="Product Numbers")
    mfr_main_nums = tables.Column(verbose_name="Main Manufacturer Numbers")
    mfr_sub_nums = tables.Column(verbose_name="Sub Manufacturer Numbers")


class ProdCateTable(tables.Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
