import django_tables2 as tables
from django.db.models import Case, F, QuerySet, Value, When
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

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
                <i class="bi bi-pencil-square"></i>
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
    or_func = tables.Column(verbose_name="功能", empty_values=(), orderable=False)

    or_mfr_username = tables.Column(
        verbose_name="訂貨人員", empty_values=(), orderable=False
    )

    or_mfr_id = tables.Column(
        verbose_name=_("廠商名稱"), empty_values=(), orderable=False, default=""
    )
    or_prod_no = tables.Column(
        verbose_name=_("商品編號"), accessor="or_prod_no", default=""
    )

    or_prod_cate_no = tables.Column(
        verbose_name=_("商品類別"), accessor="or_prod_cate_no", default=""
    )

    def render_or_func(self, record):
        return format_html(
            # <a href='{reverse(viewname="order_update", kwargs={"pk": record.pk})}' class='btn btn-info'>
            f"""
            <div class="d-flex flex-column">
            <a href='#' class='btn btn-info'>
                <i class="bi-pencil-square"></i>
                <span class="ms-1">
                編輯
                </span>
            </a>
            <a href='#' class='btn btn-info'>
                <i class="bi-trash"></i>
                <span class="ms-1">
                刪除
                </span>
            </a>
            </div>
            """
        )

    def render_or_mfr_username(self, record):
        if record.or_type == OrderRuleTypeChoices.Product:
            return record.or_prod_no.prod_mfr_id.mfr_user_id
        if record.or_type == OrderRuleTypeChoices.Manufacturer:
            return record.or_mfr_id.mfr_user_id
        return ""

    def render_or_mfr_id(self, record):
        if record.or_type == OrderRuleTypeChoices.Product:
            return record.or_prod_no.prod_mfr_id
        elif record.or_type == OrderRuleTypeChoices.Manufacturer:
            return record.or_mfr_id
        return ""

    class Meta:
        model = OrderRule
        fields = [
            "or_type",
            "or_prod_no",
            "or_prod_cate_no",
            "or_mfr_id",
            "or_cannot_order",
            "or_shipped_as_case",
            "or_order_price",
            "or_order_cases_quantity",
            "or_effective_start_date",
            "or_effective_end_date",
        ]

        sequence = (
            "or_func",
            "or_type",
            "or_prod_no",
            "or_prod_cate_no",
            "or_mfr_id",
            "or_mfr_username",
            "or_cannot_order",
            "or_shipped_as_case",
            "or_order_price",
            "or_order_cases_quantity",
            "or_effective_start_date",
            "or_effective_end_date",
        )


class SummingColums(tables.Column):
    def render_footer(self, bound_column, table):
        return format_html(
            f"""
            <input type='number' class="form-control-plaintext" value='0' field='{bound_column.name}'/>"""
        )


class CirculatedOrderTable(tables.Table):
    co_feedback = tables.Column(
        verbose_name="回饋",
        empty_values=(),
        orderable=False,
        attrs={
            "td": {"style": "min-width: 320px", "class": "d-none"},
            "th": {"class": "d-none"},
        },
    )

    co_func = tables.Column(verbose_name="功能", empty_values=(), footer="合計")
    co_total_quantity = tables.Column(
        verbose_name="庫存合計", empty_values=(), orderable=False
    )
    co_order_quantity = tables.Column(
        verbose_name="訂貨數量", empty_values=(), orderable=True
    )
    co_box_quantity = tables.Column(
        verbose_name="收縮 / 箱入數", empty_values=(), orderable=False
    )
    co_order_box_quantity = SummingColums(
        verbose_name="訂貨箱數", empty_values=(), orderable=False
    )
    co_order_cost_price = SummingColums(
        verbose_name="訂貨未稅金額", empty_values=(), orderable=False
    )
    co_prod_cost_price = tables.Column(
        verbose_name="商品未稅金額", empty_values=(), orderable=False
    )

    def render_co_feedback(self, record):
        return format_html("<div field='feedback'></div>")

    def render_co_prod_cost_price(self, record, value):
        return format_html(
            f"""
            <input type="number" readonly class="form-control-plaintext" value="{record.prod_cost_price}" field="prod-cost-price"/>"""
        )

    def render_co_order_box_quantity(self, record, value):
        return format_html(
            """
            <input type="number" readonly class="form-control-plaintext" value="0" field="order-box-quantity" />"""
        )

    def render_co_order_cost_price(self, record, value):
        if value is None:
            value = 0
        return format_html(
            f"""
            <input type="number" readonly class="form-control-plaintext" value="{value}" field="order-cost-price"/>"""
        )

    def render_co_box_quantity(self, record, value):
        return format_html(
            f"""
            <input type="number" readonly class="form-control-plaintext" value="{record.prod_outer_quantity}" field="outer-quantity"/>
            <input type="number" readonly class="form-control-plaintext" value="{record.prod_inner_quantity}" field="inner-quantity"/>"""
        )

    def render_co_total_quantity(self, record, value):
        return format_html(
            f"""
            <input type="number" readonly class="form-control-plaintext" value="{record.prod_quantity}" field="total-quantity"/>"""
        )

    def render_co_order_quantity(self, record, value):
        request = self.request
        [[_, checklist]] = request.session.get("checklist")
        checklist_dict = {c["prod_no"]: c["order_quantity"] for c in checklist}
        order_quantity = checklist_dict.get(record.prod_no, 0)

        return format_html(
            f"""
            <input type="number" class="form-control" value="{order_quantity}" field="order-quantity"/>"""
        )

    def render_prod_quantity(self, record, value):
        return format_html(
            f"""
            <input type="number" readonly class="form-control-plaintext" value="{value}" field="prod-quantity"/>"""
        )

    def render_co_func(self, record):
        request = self.request
        checked = ""
        if "checklist" in request.session:
            # TODO: why is it nested?
            [[_, checklist]] = request.session.get("checklist")
            checklist_prod_no_list = [c["prod_no"] for c in checklist]
            checked = "checked" if record.prod_no in checklist_prod_no_list else checked
        return format_html(
            f"""
            <input class="form-check-input form-control" type="checkbox" value="" {checked}>"""
        )

    def order_co_func(self, queryset: QuerySet, is_descending):
        request = self.request
        if "checklist" in request.session and queryset.exists():
            [checklist_tuple] = request.session.get("checklist")
            mfr_full_id, checklist = checklist_tuple
            checklist_prod_no_list = [c["prod_no"] for c in checklist]
            if mfr_full_id == queryset.first().prod_mfr_id.mfr_full_id:
                queryset = queryset.order_by(
                    Case(
                        When(
                            prod_no__in=checklist_prod_no_list,
                            then=1 if is_descending else 0,
                        ),
                        default=0 if is_descending else 1,
                    )
                )

            else:
                pass

        return (queryset, True)

    def order_co_order_quantity(self, queryset: QuerySet, is_descending):
        request = self.request
        if "checklist" in request.session and queryset.exists():
            [checklist_tuple] = request.session.get("checklist")
            _, checklist = checklist_tuple
            queryset = queryset.order_by(
                Case(
                    *[
                        When(
                            prod_no=c["prod_no"],
                            then=(
                                -Value(c["order_quantity"])
                                if is_descending
                                else Value(c["order_quantity"])
                            ),
                        )
                        for c in checklist
                    ],
                    default=0,
                )
            )

        return (queryset, True)

    class Meta:
        model = Prod
        fields = [
            "co_feedback",
            "co_func",
            "prod_no",
            "prod_name",
            "prod_quantity",
        ]
        per_page = 10
        row_attrs = {"data-id": lambda record: record.pk}
