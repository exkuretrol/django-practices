import django_tables2 as tables
from django.urls import reverse
from django.utils import timezone
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
    od_prod = tables.Column(verbose_name="商品", empty_values=(), orderable=False)
    od_mfr_id = tables.Column(
        verbose_name="廠商", orderable=False, accessor="od_mfr_id"
    )
    od_date = tables.Column(verbose_name="訂貨日期", accessor="od_date")
    od_except_arrival_date = tables.Column(
        verbose_name="預期到貨日", accessor="od_except_arrival_date"
    )
    od_has_contact_form = tables.Column(verbose_name="聯絡單")

    def convert_datetime_to_local_datetime(self, dt: timezone.datetime):
        tz = timezone.get_current_timezone()
        return dt.astimezone(tz)

    def render_od_prod(self, record):
        ops = record.orderprod_set.all()
        prods = []
        for op in ops:
            prods.append(
                f"""
                <label for='prod-{op.op_prod_no.prod_no}'>{op.op_prod_no.prod_name}</label>
                <input type='number' id='prod-{op.op_prod_no.prod_no}' value={op.op_quantity} />
                """
            )
        return format_html("<br>".join(prods))

    def render_od_quantity(self, record):
        ops = record.orderprod_set.all()
        inputs = []
        for op in ops:
            inputs.append(f"<input type='number' value={op.op_quantity} />")
        return format_html("".join(inputs))

    def render_od_mfr_id(self, value):
        return format_html(f"{value.mfr_full_id}<br>{value.mfr_name}")

    def render_od_selected(self, value):
        return format_html(
            f"<input type='checkbox' class='position-absolute top-50 start-50 translate-middle w-75 h-75' />"
        )

    def render_od_func(self, record):
        return format_html(
            f"<a href='{reverse(viewname="order_update", kwargs={"pk": record.pk})}' class='btn btn-info'>編輯訂單</a>"
        )

    def render_od_date(self, value):
        date = self.convert_datetime_to_local_datetime(value).strftime('%Y-%m-%d')
        return format_html(f"{date}")

    def render_od_except_arrival_date(self, value):
        return format_html(f"<input type='date' value={value} />")

    def render_od_has_contact_form(self, value):
        if value:
            return "聯絡單"
        return ""

    class Meta:
        model = Order
        fields = []
        sequence = (
            "od_selected",
            "od_func",
            "od_no",
            "od_prod",
            "od_mfr_id",
            "od_date",
            "od_except_arrival_date",
            "od_has_contact_form",
        )
        attrs = {"class": "table table-striped table-bordered table-hover"}
        row_attrs = {"data-id": lambda record: record.pk}
