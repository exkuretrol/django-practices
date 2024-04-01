import django_tables2 as tables
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from manufacturer.models import Manufacturer
from prod.models import Prod

from .models import Order, OrderRule, OrderRuleTypeChoices


class OrderTable(tables.Table):
    od_func = tables.Column(verbose_name="功能", empty_values=(), orderable=False)
    od_no = tables.Column(verbose_name="訂單編號", accessor="od_no")
    # od_prod = tables.Column(verbose_name="商品", empty_values=(), orderable=False)
    # od_mfr_id = tables.Column(
    #     verbose_name="廠商", orderable=False, accessor="od_mfr_id"
    # )
    od_date = tables.Column(
        verbose_name="訂貨日期", accessor="od_date", order_by=["od_no"]
    )
    od_except_arrival_date = tables.Column(
        verbose_name="預期到貨日", accessor="od_except_arrival_date"
    )
    od_has_contact_form = tables.Column(verbose_name="聯絡單")

    def convert_datetime_to_local_datetime(self, dt: timezone.datetime):
        tz = timezone.get_current_timezone()
        return dt.astimezone(tz)

    # def render_od_prod(self, record):
    #     ops = record.orderprod_set.all()
    #     prods = []
    #     for op in ops:
    #         prods.append(
    #             f"""
    #             <p class="m-0"><a href={reverse("prod_detail", kwargs={"pk":op.op_prod_no.pk})}>{op.op_prod_no.prod_name} ➡ {op.op_quantity}</a></p>
    #             """
    #         )
    #     return format_html("".join(prods))

    def render_od_quantity(self, record):
        ops = record.orderprod_set.all()
        inputs = []
        for op in ops:
            inputs.append(f"<input type='number' value={op.op_quantity} />")
        return format_html("".join(inputs))

    # def render_od_mfr_id(self, value):
    #     return format_html(f"{value.mfr_full_id}<br>{value.mfr_name}")

    def render_od_selected(self, value):
        return format_html(
            f"<input type='checkbox' class='position-absolute top-50 start-50 translate-middle w-75 h-75' />"
        )

    def render_od_func(self, record):
        return format_html(
            f"""
            <a href='{reverse(viewname="order_update", kwargs={"pk": record.pk})}' class='btn btn-info'>
                <svg class="bi" width="16" height="16" role="img" aria-label="pencil-square" fill="currentColor">
                    <use xlink:href="{static("sprite/bootstrap-icons.svg")}#pencil-square"/>
                </svg>
                <span class="ms-1">
                編輯
                </span>
            </a>"""
        )

    def render_od_date(self, value):
        date = self.convert_datetime_to_local_datetime(value).strftime("%Y-%m-%d")
        return format_html(f"{date}")

    def render_od_except_arrival_date(self, value):
        return format_html(f"{value}")

    def render_od_has_contact_form(self, value):
        if value:
            return "聯絡單"
        return ""

    class Meta:
        model = Order
        fields = []
        sequence = (
            "od_func",
            "od_no",
            # "od_prod",
            # "od_mfr_id",
            "od_date",
            "od_except_arrival_date",
            "od_has_contact_form",
        )
        attrs = {"class": "table table-striped table-bordered table-hover"}
        row_attrs = {"data-id": lambda record: record.pk}
        order_by = ("-od_no",)


class OrderRulesTable(tables.Table):
    # or_func = tables.Column(verbose_name="功能", empty_values=(), orderable=False)

    or_mfr_username = tables.Column(
        verbose_name="訂貨人員", empty_values=(), orderable=False
    )

    or_mfr_name = tables.Column(
        verbose_name="廠商名稱", empty_values=(), orderable=False
    )

    or_prod_name = tables.Column(
        verbose_name="商品名稱", empty_values=(), orderable=False
    )

    def render_or_func(self, record):
        return format_html(
            # <a href='{reverse(viewname="order_update", kwargs={"pk": record.pk})}' class='btn btn-info'>
            f"""
            <div class="d-flex flex-column">
            <a href='#' class='btn btn-info'>
                <svg class="bi" width="16" height="16" role="img" aria-label="pencil-square" fill="currentColor">
                    <use xlink:href="{static("sprite/bootstrap-icons.svg")}#pencil-square"/>
                </svg>
                <span class="ms-1">
                編輯
                </span>
            </a>
            <a href='#' class='btn btn-info'>
                <svg class="bi" width="16" height="16" role="img" aria-label="pencil-square" fill="currentColor">
                    <use xlink:href="{static("sprite/bootstrap-icons.svg")}#trash"/>
                </svg>
                <span class="ms-1">
                刪除
                </span>
            </a>
            </div>
            """
        )

    def render_or_prod_name(self, record):
        if record.or_type == OrderRuleTypeChoices.Product:
            prod = Prod.objects.get(prod_no=record.or_object_id)
            return prod
        return ""

    def render_or_mfr_username(self, record):
        if record.or_type == OrderRuleTypeChoices.Product:
            prod = Prod.objects.get(prod_no=record.or_object_id)
            return prod.prod_mfr_id.mfr_user_id.username
        if record.or_type == OrderRuleTypeChoices.Manufacturer:
            mfr = Manufacturer.objects.get(mfr_id=record.or_object_id)
            return mfr.mfr_user_id.username
        return ""

    def render_or_mfr_name(self, record):
        if record.or_type == OrderRuleTypeChoices.Product:
            prod = Prod.objects.get(prod_no=record.or_object_id)
            return prod.prod_mfr_id
        if record.or_type == OrderRuleTypeChoices.Manufacturer:
            mfr = Manufacturer.objects.get(mfr_id=record.or_object_id)
            return mfr

        return ""

    class Meta:
        model = OrderRule
        fields = [
            "or_id",
            "or_type",
            "or_object_id",
            "or_cannot_order",
            "or_cannot_be_shipped_as_case",
            "or_order_amount",
            "or_order_quantity_cases",
            "or_effective_start_date",
            "or_effective_end_date",
        ]

        sequence = (
            # "or_func",
            "or_type",
            "or_object_id",
            "or_prod_name",
            "or_mfr_name",
            "or_cannot_order",
            "or_cannot_be_shipped_as_case",
            "or_order_amount",
            "or_order_quantity_cases",
            "or_effective_start_date",
            "or_effective_end_date",
        )
