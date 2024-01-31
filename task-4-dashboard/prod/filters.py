import django_filters as filters
from .models import Prod, TypesInProd, StatusInProd
from django.forms import widgets


class ProdNoFilter(filters.FilterSet):
    prod_no = filters.BaseInFilter(label="Product No", lookup_expr="in", required=False)
    class Meta:
        model = Prod
        fields = ["prod_no"]

class ProdFilter(filters.FilterSet):
    prod_name = filters.CharFilter(label="Name", lookup_expr="icontains")
    prod_desc = filters.CharFilter(label="Description", lookup_expr="icontains")
    prod_quantity = filters.NumberFilter(label="Quantity =")
    prod_quantity__gte = filters.NumberFilter(label="Quantity ≥")
    prod_quantity__lte = filters.NumberFilter(label="Quantity ≤")
    prod_type = filters.ChoiceFilter(label="Type", choices=TypesInProd)
    prod_status = filters.ChoiceFilter(label="Status", choices=StatusInProd)

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        for field in self.form.fields:
            widget = self.form.fields[field].widget
            if widget.input_type in ["text", "number", "select"]:
                widget.attrs.update({"class": "input-normal"})

    class Meta:
        model = Prod
        exclude = ["prod_img"]
        fields = [
            "prod_name",
            "prod_desc",
            "prod_quantity",
            "prod_quantity__gte",
            "prod_quantity__lte",
            "prod_type",
            "prod_status",
        ]
