import csv
import datetime
from io import StringIO

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from dal import autocomplete
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import inlineformset_factory, modelformset_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from manufacturer.models import Manufacturer
from prod.models import Prod, ProdRestriction

from .models import Order, OrderProd, OrderRule, OrderRuleTypeChoices


class OrderUpdateForm(forms.ModelForm):
    od_mfr_id = forms.CharField(
        label="廠商 ID", disabled=True, empty_value=(), widget=forms.HiddenInput()
    )
    od_mfr_full_id = forms.CharField(label="廠商編號", disabled=True, empty_value=())
    od_mfr_name = forms.CharField(label="廠商名稱", disabled=True, empty_value=())
    od_mfr_user_id_username = forms.CharField(
        label="訂貨人員", disabled=True, empty_value=()
    )

    class Meta:
        model = Order
        fields = [
            "od_no",
            "od_date",
            "od_except_arrival_date",
            "od_has_contact_form",
            "od_contact_form_no",
            "od_warehouse_storage_fee_recipient",
            "od_notes",
            "od_contact_form_notes",
        ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["od_no"].disabled = True
        self.fields["od_date"].disabled = True
        self.fields["od_mfr_id"].initial = self.instance.od_mfr_id
        self.fields["od_mfr_full_id"].initial = self.instance.od_mfr_id.mfr_full_id
        self.fields["od_mfr_name"].initial = self.instance.od_mfr_id.mfr_name
        self.fields["od_mfr_user_id_username"].initial = (
            self.instance.od_mfr_id.mfr_user_id.username
        )

    field_order = [
        "od_no",
        "od_mfr_user_id_username",
        "od_mfr_id",
        "od_mfr_full_id",
        "od_mfr_name",
        "od_date",
        "od_except_arrival_date",
        "od_notes",
        "od_has_contact_form",
        "od_contact_form_no",
        "od_warehouse_storage_fee_recipient",
        "od_contact_form_notes",
    ]

    def clean(self):
        data = self.cleaned_data
        if data["od_except_arrival_date"] < data["od_date"].date():
            raise forms.ValidationError(
                _("Except arrival date should be later than order date."),
                code="invalid_except_arrival_date",
            )
        return super().clean()


class OrderProdUpdateForm(forms.ModelForm):
    op_prod = forms.CharField(label="產品名稱", disabled=True, empty_value=())

    class Meta:
        model = OrderProd
        fields = ["op_quantity", "op_status"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.instance.op_prod_no:
            self.fields["op_prod"].initial = self.instance.op_prod_no.prod_name

    field_order = ["op_prod", "op_quantity", "op_status"]


class OrderProdCreateForm(forms.ModelForm):
    op_prod = forms.CharField(
        label="產品名稱", disabled=True, empty_value=(), required=False
    )
    op_prod_no = forms.CharField(widget=forms.HiddenInput())
    op_od_no = forms.CharField(widget=forms.HiddenInput())

    def clean_op_prod_no(self):
        op_prod_no_object = Prod.objects.get(pk=self.cleaned_data["op_prod_no"])
        return op_prod_no_object

    def clean_op_od_no(self):
        op_od_no_object = Order.objects.get(pk=self.cleaned_data["op_od_no"])
        return op_od_no_object

    def clean(self):
        self.pr = self.get_prod_restriction()
        self.check_order_rule_prod()
        self.check_order_rule_mfr()
        self.check_order_rule_prod_cate()
        return super().clean()

    def get_prod_restriction(self):
        pr = None
        try:
            pr = ProdRestriction.objects.get(
                pr_prod_no=self.cleaned_data["op_prod_no"],
                pr_effective_start_date__lte=timezone.now().date(),
                pr_effective_end_date__gte=timezone.now().date(),
            )
        except ProdRestriction.DoesNotExist:
            pass
        return pr

    def get_rule(self, or_type: OrderRuleTypeChoices):
        rule = None
        try:
            rule = OrderRule.objects.filter(
                or_type=or_type,
                or_prod_no=self.cleaned_data["op_prod_no"],
                or_effective_start_date__lte=timezone.now(),
                or_effective_end_date__gte=timezone.now(),
            )
        except OrderRule.DoesNotExist:
            pass
        return rule

    def check_order_rule_prod(self):
        rule = self.get_rule(OrderRuleTypeChoices.Product)
        if rule.exists():
            if self.pr is None:
                self.add_error(
                    field=NON_FIELD_ERRORS,
                    error=forms.ValidationError(
                        _("商品限制未定義，但是訂單規則已經定義。")
                    ),
                )
            else:
                # TODO: how about multiple order rules?
                a_rule = rule.first()
                order_price = self.pr.pr_unit_price * self.cleaned_data["op_quantity"]
                case_num = (
                    self.cleaned_data["op_quantity"] / self.pr.pr_as_case_quantity
                )
                if a_rule.or_cannot_order:
                    self.add_error(
                        field=NON_FIELD_ERRORS,
                        error=forms.ValidationError(
                            _("商品 %(prod_name)s 不能訂貨。"),
                            code="prod_cannot_order",
                            params={
                                "prod_name": self.cleaned_data["op_prod_no"].prod_name
                            },
                        ),
                    )
                    return
                if a_rule.or_order_amount is not None and a_rule.or_order_amount > 0:
                    if order_price < a_rule.or_order_amount:
                        self.add_error(
                            field=NON_FIELD_ERRORS,
                            error=forms.ValidationError(
                                _(
                                    "商品 %(prod_name)s 訂貨金額不足。單價 %(unit_price)d 元，數量 %(quantity)d 個，共 %(order_price)d 元。根據訂貨規則 %(order_rule_no)d，至少需要 %(order_amount)d 元。"
                                ),
                                code="prod_order_amount_not_enough",
                                params={
                                    "prod_name": self.cleaned_data[
                                        "op_prod_no"
                                    ].prod_name,
                                    "quantity": self.cleaned_data["op_quantity"],
                                    "unit_price": self.pr.pr_unit_price,
                                    "order_price": order_price,
                                    "order_rule_no": a_rule.or_id,
                                    "order_amount": a_rule.or_order_amount,
                                },
                            ),
                        )
                if not a_rule.or_cannot_be_shipped_as_case:
                    if a_rule.or_order_quantity_cases > 0:
                        if not case_num.is_integer():
                            self.add_error(
                                field=NON_FIELD_ERRORS,
                                error=forms.ValidationError(
                                    _(
                                        "商品 %(prod_name)s 訂貨箱數不是整數。目前只有 %(case_num).2f 箱。每箱至少需要 %(as_case_quantity)d 個商品才成箱。"
                                    ),
                                    params={
                                        "prod_name": self.cleaned_data[
                                            "op_prod_no"
                                        ].prod_name,
                                        "case_num": case_num,
                                        "as_case_quantity": self.pr.pr_as_case_quantity,
                                    },
                                ),
                            )
                        if case_num < a_rule.or_order_quantity_cases:
                            self.add_error(
                                field=NON_FIELD_ERRORS,
                                error=forms.ValidationError(
                                    _(
                                        "商品 %(prod_name)s 訂貨箱數不足。至少需要 %(quantity)d 箱，目前只有 %(case_num).2f 箱。每箱至少需要 %(as_case_quantity)d 個商品才成箱。"
                                    ),
                                    code="prod_order_quantity_cases_not_enough",
                                    params={
                                        "prod_name": self.cleaned_data[
                                            "op_prod_no"
                                        ].prod_name,
                                        "case_num": case_num,
                                        "quantity": a_rule.or_order_quantity_cases,
                                        "as_case_quantity": self.pr.pr_as_case_quantity,
                                    },
                                ),
                            )

    def check_order_rule_mfr(self):
        rule = self.get_rule(OrderRuleTypeChoices.Manufacturer)
        pass
        # if rule is not None:
        #     pass

    def check_order_rule_prod_cate(self):
        rule = self.get_rule(OrderRuleTypeChoices.ProductCategory)
        pass
        # if rule is not None:
        #     pass

    class Meta:
        model = OrderProd
        fields = ["op_od_no", "op_prod_no", "op_quantity"]

    field_order = ["op_prod", "op_quantity"]


OrderProdUpdateFormset = inlineformset_factory(
    parent_model=Order,
    model=OrderProd,
    form=OrderProdUpdateForm,
    can_delete=True,
    can_delete_extra=True,
    extra=0,
)


OrderProdCreateFormset = modelformset_factory(
    model=OrderProd,
    form=OrderProdCreateForm,
    can_delete=True,
    can_delete_extra=True,
    extra=0,
)


def validate_tsv(input_text: str) -> None:
    f = StringIO(input_text)
    csv_reader = csv.reader(f, delimiter="\t")
    headers = next(csv_reader)
    column_num = len(headers)
    if column_num == 1:
        raise forms.ValidationError(
            _("Please use tab as delimiter."), code="invalid_tsv"
        )
    elif column_num > 2:
        raise forms.ValidationError(
            _("Each row should have 2 columns."), code="invalid_format"
        )
    for row in csv_reader:
        if len(row) != column_num:
            raise forms.ValidationError(
                _(
                    "Each row should have the same number of columns.",
                    code="invalid_row",
                )
            )


class OrderBeforeCreateForm(forms.Form):
    clipblard_placeholder = _(
        f"""Your clipboard should look like this:
prod_no\tquantity
144239\t10
144240\t2

note: it should not contain the header row. 
"""
    )
    clipboard = forms.CharField(
        strip=False,
        widget=forms.Textarea(attrs={"placeholder": clipblard_placeholder}),
        validators=[validate_tsv],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", _("Submit")))

    def clean_clipboard(self):
        input_text = self.cleaned_data["clipboard"]
        orders_to_be_updated = dict()
        f = StringIO(input_text)
        csv_reader = csv.reader(f, delimiter="\t")
        for row in csv_reader:
            prod_no, prod_quantity = row
            try:
                prod_no = int(prod_no)
            except:
                self.add_error(
                    self.fields["clipboard"].label,
                    forms.ValidationError(
                        _("Product number should be an integer."),
                        code="invalid_prod_no",
                    ),
                )
                continue

            prod = Prod.objects.filter(prod_no=prod_no)
            if not prod.exists():
                self.add_error(
                    self.fields["clipboard"].label,
                    forms.ValidationError(
                        _(
                            "Product number %(prod_no)s does not exist. Please check again."
                        ),
                        code="prod_no_not_exist",
                        params={"prod_no": prod_no},
                    ),
                )
                continue

            try:
                prod_quantity = int(prod_quantity)
            except:
                self.add_error(
                    self.fields["clipboard"].label,
                    forms.ValidationError(
                        _("Product quantity should be an integer."),
                        code="invalid_prod_quantity",
                    ),
                )

            if prod_quantity <= 0:
                self.add_error(
                    self.fields["clipboard"].label,
                    forms.ValidationError(
                        _(
                            "Product quantity should be greater than 0. Please check the prod %(prod_no)s again."
                        ),
                        code="invalid_prod_quantity",
                        params={"prod_no": prod_no},
                    ),
                )

            if prod_no in orders_to_be_updated:
                self.add_error(
                    self.fields["clipboard"].label,
                    forms.ValidationError(
                        _(
                            "Product %(prod_no)s has been duplicated. Please check again."
                        ),
                        code="duplicated_prod_no",
                        params={"prod_no": prod_no},
                    ),
                )
            orders_to_be_updated.update(
                {
                    prod_no: {
                        "quantity": prod_quantity,
                        "mfr_id": prod.first().prod_mfr_id.mfr_id,
                    }
                }
            )

        grouped_orders = {}
        # TODO: if same manufacturer has more than five products, it should be split into multiple orders
        for prod_no, order_info in orders_to_be_updated.items():
            mfr_id = order_info["mfr_id"]
            if mfr_id not in grouped_orders:
                grouped_orders[mfr_id] = list()
            grouped_orders[mfr_id].append(
                {"prod_no": prod_no, "quantity": order_info["quantity"]}
            )
        return grouped_orders

    def clean(self):
        return super().clean()


def get_order_no_from_day(day=timezone.localdate(), mode: str = "startswith"):
    # TODO: order and timezone.now().date() didn't not sync,
    #       if user enter the order create page at 23:59:59,
    #       and then create an order at 00:00:00 (the form failed, and the user re-enter the form),
    #       the od_date will update, but the od_no didn't.
    day_str = day.strftime("%Y%m%d")

    # Month + 30
    # YYYYmmdd
    # 0123^
    day_str_list = list(day_str)
    day_str_list[4] = str(int(day_str[4]) + 3)
    day_str = "".join(day_str_list)

    if mode == "day":
        orders = Order.objects.filter(od_date__date__exact=day)
    elif mode == "range":
        orders = Order.objects.filter(
            od_date__range=(day, day + datetime.timedelta(days=1))
        )
    elif mode == "startswith":
        orders = Order.objects.filter(od_no__startswith=day_str)

    if orders.exists():
        order_no = orders.last().od_no
    else:
        order_no = int(day_str + "00000")
    return order_no


class OrderCreateForm(forms.ModelForm):
    od_mfr_full_id = forms.CharField(
        label="廠商編號", disabled=True, empty_value=(), required=False
    )
    od_mfr_name = forms.CharField(
        label="廠商名稱", disabled=True, empty_value=(), required=False
    )
    od_mfr_user_id_username = forms.CharField(
        label="訂貨人員", disabled=True, empty_value=(), required=False
    )
    od_mfr_id = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Order
        fields = "__all__"

    field_order = [
        "od_no",
        "od_mfr_user_id_username",
        "od_mfr_full_id",
        "od_mfr_name",
        "od_date",
        "od_except_arrival_date",
        "od_notes",
        "od_has_contact_form",
        "od_contact_form_no",
        "od_warehouse_storage_fee_recipient",
        "od_contact_form_notes",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["od_except_arrival_date"].initial = (
            timezone.now() + datetime.timedelta(days=7)
        ).date()
        for name, field in self.fields.items():
            if name in ["od_no", "od_date"]:
                field.widget.attrs.update(
                    {"class": "pe-none", "tabindex": "-1", "aria-disabled": "true"}
                )

    def clean_od_mfr_id(self):
        od_mfr_id_object = Manufacturer.objects.get(pk=self.cleaned_data["od_mfr_id"])
        return od_mfr_id_object

    def clean(self):
        data = self.cleaned_data
        if data["od_except_arrival_date"] < data["od_date"].date():
            raise forms.ValidationError(
                _("Except arrival date should be later than order date."),
                code="invalid_except_arrival_date",
            )
        return super().clean()


OrderFormset = modelformset_factory(Order, OrderCreateForm, extra=3)


class OrderRuleCreateForm(forms.ModelForm):
    # TODO: check effective start / end date overlap
    class Meta:
        fields = "__all__"
        model = OrderRule
        widgets = {
            "or_prod_no": autocomplete.ModelSelect2(url="prod_autocomplete"),
            "or_mfr_id": autocomplete.ModelSelect2(url="mfr_autocomplete"),
            "or_prod_cate_no": autocomplete.ModelSelect2(
                url="prod_all_cate_autocomplete"
            ),
        }


class CirculatedOrderManufacturerForm(forms.ModelForm):
    mfr_id = forms.ChoiceField(choices=(), label="廠商名稱")

    class Meta:
        model = Manufacturer
        fields = ["mfr_id"]

    def __init__(self, choices, initial=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["mfr_id"].choices = choices
        if initial:
            self.fields["mfr_id"].initial = choices[initial]
