from django import forms
from django.forms import inlineformset_factory

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


OrderProdFormSet = inlineformset_factory(
    parent_model=Order,
    model=OrderProd,
    form=OrderProdsForm,
    can_delete=True,
    can_delete_extra=True,
    extra=0,
)
