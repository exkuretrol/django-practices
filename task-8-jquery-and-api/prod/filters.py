import django_filters as filters

from .models import Prod


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
    prod_cate_no__cate_no = filters.CharFilter(
        label="Category No", lookup_expr="icontains"
    )
    # prod_type = filters.ChoiceFilter(label="Type", choices=TypesChoices)
    # prod_status = filters.ChoiceFilter(label="Status", choices=StatusInProd)

    class Meta:
        model = Prod
        exclude = ["prod_img"]
        fields = [
            "prod_name",
            "prod_desc",
            "prod_quantity",
            "prod_quantity__gte",
            "prod_quantity__lte",
            "prod_cate_no__cate_no",
            # "prod_status",
        ]
