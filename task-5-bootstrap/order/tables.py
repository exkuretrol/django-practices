import django_tables2 as tables
from django.utils.html import format_html

from .models import Order


class OrderTable(tables.Table):
    od_selected = tables.Column(
        verbose_name="選擇",
        empty_values=(),
        orderable=False,
        attrs={"td": {"class": "position-relative"}},
    )
    od_func = tables.Column(verbose_name="功能", empty_values=(), orderable=False)
    od_no = tables.Column(verbose_name="訂單編號", accessor="od_no", orderable=False)
    od_prod = tables.Column(verbose_name="商品", orderable=False)
    od_mfr = tables.Column(verbose_name="廠商", orderable=False)
    od_quantity = tables.Column(verbose_name="訂貨數量")
    od_date = tables.Column(verbose_name="訂貨日期", accessor="od_date")
    od_except_arrival_date = tables.Column(
        verbose_name="預期到貨日", accessor="od_except_arrival_date"
    )
    od_has_contact_form = tables.Column(verbose_name="聯絡單")

    def render_od_prod(self, value, record):
        return format_html(f"{value.pk}<br>{record.od_prod_no.prod_name}")

    def render_od_mfr(self, value, record):
        return format_html(f"{value.mfr_full_id}<br>{record.od_mfr_id.mfr_name}")

    def render_od_selected(self, value):
        return format_html(
            f"<input type='checkbox' class='position-absolute top-50 start-50 translate-middle w-75 h-75' />"
        )

    def render_od_func(self, value):
        return format_html(f"<a href='#' class='btn btn-info'>編輯訂單</a>")

    def render_od_quantity(self, value):
        return format_html(f"<input type='number' value={value} />")

    def render_od_except_arrival_date(self, value):
        return format_html(f"<input type='date' value={value} />")

    def render_od_has_contact_form(self, value):
        if value:
            return "聯絡單"
        return ""

    class Meta:
        model = Order
        fields = []
        attrs = {"class": "table table-striped table-bordered table-hover"}
        row_attrs = {"data-id": lambda record: record.pk}
