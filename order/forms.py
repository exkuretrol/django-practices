import csv
import datetime
import logging
from io import StringIO

from crispy_forms.helper import FormHelper
from dal import autocomplete
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import inlineformset_factory, modelformset_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from manufacturer.models import Manufacturer
from prod.models import Prod
from utils.order import OrderProdSchema, check_product_rule

from .models import Order, OrderProd, OrderRule

logger = logging.getLogger(__name__)


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
        prod_dict = {
            "prod_no": self.cleaned_data["op_prod_no"],
            "prod_quantity": self.cleaned_data["op_quantity"],
        }
        prod = OrderProdSchema(**prod_dict)
        logger.debug(prod)

        error_list = check_product_rule(prod)
        logger.debug(f"product rule check: {error_list}")

        for error in error_list:
            self.add_error(
                "op_quantity",
                forms.ValidationError(error["message"], code=error["code"]),
            )

        return super().clean()

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
        widget=forms.HiddenInput,
        # validators=[validate_tsv],
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "get"

    def clean_clipboard(self):
        input_text = self.cleaned_data["clipboard"]
        prods_dict = dict()
        f = StringIO(input_text)
        f2 = StringIO(input_text)
        csv_reader = csv.reader(f, delimiter="\t")
        csv_reader_ = csv.reader(f2, delimiter="\t")
        headers = next(csv_reader_)
        column_num = len(headers)
        if column_num == 1:
            self.add_error(
                NON_FIELD_ERRORS,
                forms.ValidationError(
                    _("請使用 Tab 作為分隔符號。"), code="invalid_tsv"
                ),
            )
            return
        elif column_num > 2:
            self.add_error(
                NON_FIELD_ERRORS,
                forms.ValidationError(
                    _("每列應該有 2 欄組成。"), code="invalid_format"
                ),
            )
            return
        for row in csv_reader_:
            if len(row) != column_num:
                self.add_error(
                    NON_FIELD_ERRORS,
                    forms.ValidationError(
                        _(
                            "每列應該有相同數量的欄位數。",
                            code="invalid_row",
                        )
                    ),
                )
                return
        for row in csv_reader:
            prod_no, prod_quantity = row
            try:
                prod_no = int(prod_no)
            except:
                self.add_error(
                    NON_FIELD_ERRORS,
                    forms.ValidationError(
                        _("產品編號應該是整數。"),
                        code="invalid_prod_no",
                    ),
                )
                continue
            prod = Prod.objects.filter(prod_no=prod_no)
            if not prod.exists():
                self.add_error(
                    NON_FIELD_ERRORS,
                    forms.ValidationError(
                        _(
                            "產品編號 %(prod_no)s 不存在。請重新檢查。",
                        ),
                        code="prod_no_not_exist",
                        params={"prod_no": prod_no},
                    ),
                )
                continue
            prod = prod.first()
            try:
                prod_quantity = int(prod_quantity)
            except:
                self.add_error(
                    NON_FIELD_ERRORS,
                    forms.ValidationError(
                        _("產品數量應該是整數。"),
                        code="invalid_prod_quantity",
                    ),
                )
            if prod_quantity <= 0:
                self.add_error(
                    NON_FIELD_ERRORS,
                    forms.ValidationError(
                        _(
                            "產品數量應該大於0。請重新檢查產品 %(prod_no)s。",
                        ),
                        code="invalid_prod_quantity",
                        params={"prod_no": prod_no},
                    ),
                )
            if prod_no in prods_dict:
                self.add_error(
                    NON_FIELD_ERRORS,
                    forms.ValidationError(
                        _(
                            "產品 %(prod_no)s 已重複。請重新檢查。",
                        ),
                        code="duplicated_prod_no",
                        params={"prod_no": prod_no},
                    ),
                )
            prods_dict.update(
                {
                    prod_no: {
                        "quantity": prod_quantity,
                        "mfr_id": prod.prod_mfr_id.mfr_id,
                    }
                }
            )
        grouped_orders = {}
        mfr_count = {}

        for prod_no, order_info in prods_dict.items():
            mfr_id = str(order_info["mfr_id"])
            if mfr_id not in mfr_count:
                mfr_count.update({mfr_id: 0})
            else:
                mfr_id = mfr_id + "_" * mfr_count[mfr_id]

            if mfr_id in grouped_orders and len(grouped_orders[mfr_id]) >= 5:
                mfr_count[mfr_id] += 1
                mfr_id += "_"

            if mfr_id not in grouped_orders:
                grouped_orders.update({mfr_id: []})

            grouped_orders[mfr_id].append(
                {"prod_no": prod_no, "quantity": order_info["quantity"]}
            )
        return grouped_orders

    def clean(self):
        return super().clean()


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
