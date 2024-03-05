import csv
import datetime
from io import StringIO

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import formset_factory, inlineformset_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
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


class OrderProdsForm(forms.ModelForm):
    op_prod = forms.CharField(label="產品名稱", disabled=True, empty_value=())

    class Meta:
        model = OrderProd
        fields = ["op_quantity"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["op_prod"].initial = self.instance.op_prod_no.prod_name

    field_order = ["op_prod", "op_quantity"]


OrderProdFormset = inlineformset_factory(
    parent_model=Order,
    model=OrderProd,
    form=OrderProdsForm,
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
        widget=forms.HiddenInput(attrs={"placeholder": clipblard_placeholder}),
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

            if not Prod.objects.filter(prod_no=prod_no).exists():
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
            orders_to_be_updated.update({prod_no: prod_quantity})

        return orders_to_be_updated


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def get_current_order_no(self):
        today_str = timezone.now().strftime("%Y%m%d")

        # Month + 30
        # YYYYmmdd
        # 0123^
        today_str = str(int(today_str[4]) + 3)

        lb = int(today_str + "00000")
        hb = int(today_str + "99999")
        orders = Order.objects.filter(od_no__range=(lb, hb))
        if orders.exists():
            order_no = orders.last().od_no
        else:
            order_no = int(lb)
        return order_no

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        order_no = self.get_current_order_no() + 1
        self.fields["od_no"].disabled = True
        self.fields["od_no"].widget = forms.TextInput()
        self.fields["od_no"].initial = order_no
        self.fields["od_except_arrival_date"].initial = (
            timezone.now().date() + datetime.timedelta(days=7)
        )
        self.fields["od_date"].disabled = True
        self.fields["od_status"].disabled = True


OrderFormset = formset_factory(OrderCreateForm)
