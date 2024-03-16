import csv
import datetime
from io import StringIO

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from manufacturer.models import Manufacturer
from prod.models import Prod

from .models import Order, OrderProd


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["od_no"].disabled = True
        self.fields["od_mfr_id"].disabled = True
        self.fields["od_date"].disabled = True


class OrderProdUpdateForm(forms.ModelForm):
    op_prod = forms.CharField(label="產品名稱", disabled=True, empty_value=())

    class Meta:
        model = OrderProd
        fields = ["op_quantity"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.instance.op_prod_no:
            self.fields["op_prod"].initial = self.instance.op_prod_no.prod_name

    field_order = ["op_prod", "op_quantity"]


class OrderProdCreateForm(forms.ModelForm):
    op_prod = forms.CharField(
        label="產品名稱", disabled=True, empty_value=(), required=False
    )
    op_prod_no = forms.CharField(widget=forms.HiddenInput())
    op_od_no = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = OrderProd
        fields = ["op_od_no", "op_prod_no", "op_quantity"]

    def clean_op_prod_no(self):
        op_prod_no_object = Prod.objects.get(pk=self.cleaned_data["op_prod_no"])
        return op_prod_no_object

    def clean_op_od_no(self):
        op_od_no_object = Order.objects.get(pk=self.cleaned_data["op_od_no"])
        return op_od_no_object

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
    can_delete=False,
    can_delete_extra=False,
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
                raise forms.ValidationError(
                    _("Product number should be an integer."), code="invalid_prod_no"
                )

            prod = Prod.objects.filter(prod_no=prod_no)
            if not prod.exists():
                raise forms.ValidationError(
                    _("Product number %(prod_no)s does not exist. Please check again."),
                    code="prod_no_not_exist",
                    params={"prod_no": prod_no},
                )

            try:
                prod_quantity = int(prod_quantity)
            except:
                raise forms.ValidationError(
                    _("Product quantity should be an integer."),
                    code="invalid_prod_quantity",
                )

            if prod_quantity <= 0:
                raise forms.ValidationError(
                    _(
                        "Product quantity should be greater than 0. Please check the prod %(prod_no)s again."
                    ),
                    code="invalid_prod_quantity",
                    params={"prod_no": prod_no},
                )

            if prod_no in orders_to_be_updated:
                raise forms.ValidationError(
                    _("Product %(prod_no)s has been duplicated. Please check again."),
                    code="duplicated_prod_no",
                    params={"prod_no": prod_no},
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


def get_current_order_no():
    # TODO: order and timezone.now().date() didn't not sync,
    #       if user enter the order create page at 23:59:59,
    #       and then create an order at 00:00:00 (the form failed, and the user re-enter the form),
    #       the od_date will update, but the od_no didn't.
    today = timezone.localdate()
    today_str = today.strftime("%Y%m%d")

    # Month + 30
    # YYYYmmdd
    # 0123^
    today_str_list = list(today_str)
    today_str_list[4] = str(int(today_str[4]) + 3)
    today_str = "".join(today_str_list)

    orders = Order.objects.filter(od_date__date__exact=today)
    if orders.exists():
        order_no = orders.last().od_no
    else:
        order_no = int(today_str + "00000")
    return order_no


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["od_except_arrival_date"].initial = (
            timezone.now() + datetime.timedelta(days=7)
        ).date()
        self.fields["od_status"].disabled = True
        for name, field in self.fields.items():
            if name in ["od_mfr_id", "od_no", "od_date"]:
                field.widget.attrs.update(
                    {"class": "pe-none", "tabindex": "-1", "aria-disabled": "true"}
                )
            elif name == "od_except_arrival_date":
                field.widget = forms.DateInput(
                    format=("%Y-%m-%d"),
                )

    def clean(self):
        data = self.cleaned_data
        if data["od_except_arrival_date"] < data["od_date"].date():
            raise forms.ValidationError(
                _("Except arrival date should be later than order date."),
                code="invalid_except_arrival_date",
            )
        return super().clean()


OrderFormset = modelformset_factory(Order, OrderCreateForm, extra=3)
