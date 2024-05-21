import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
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

    def render_prod_name(self, record):
        prod_detail_url = reverse("prod_detail", kwargs={"pk": record.pk})
        return mark_safe(f"<a href={prod_detail_url}>{record.prod_name}</a>")

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
    class SummingColumn(tables.Column):
        def render_footer(self, bound_column, table):
            return sum(bound_column.accessor.resolve(row) for row in table.data)

    user_name = tables.Column(
        verbose_name="User",
        attrs={"td": {"user-id": get_user_id}},
        footer="Total",
    )

    prod_nums = SummingColumn(
        verbose_name="Product Numbers", attrs={"td": {"col": "prod_nums"}}
    )
    mfr_main_nums = SummingColumn(
        verbose_name="Main Manufacturer Numbers", attrs={"td": {"col": "mfr_main_nums"}}
    )
    mfr_sub_nums = SummingColumn(
        verbose_name="Sub Manufacturer Numbers", attrs={"td": {"col": "mfr_sub_nums"}}
    )


class ProdCateTable(tables.Table):

    user_name = tables.Column(
        verbose_name="User",
        attrs={"td": {"user-id": get_user_id}},
        footer="Total",
    )
