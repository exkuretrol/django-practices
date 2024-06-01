import django_filters
from dal import autocomplete
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from manufacturer.models import Manufacturer
from prod.models import Prod, ProdCategory

from .models import Order, OrderProd, OrderRule, OrderRuleTypeChoices


class OrderFilter(django_filters.FilterSet):
    def orderprod_prod_filter(self, queryset, name, value):
        ops = OrderProd.objects.filter(op_prod_no=value.pk)
        filtered_queryset = queryset.filter(orderprod_set__in=ops)
        return filtered_queryset

    # def orderprod_order_no_filter(self, queryset, name, value):
    # od_nos = self.request.GET.getlist("od_no")
    # return queryset
    # return queryset.filter(od_no__in=od_nos)

    od_no = django_filters.ModelChoiceFilter(
        label="訂單編號",
        required=False,
        # method="orderprod_order_no_filter",
        widget=autocomplete.ModelSelect2(
            url="order_no_autocomplete",
            attrs={
                "data-theme": "bootstrap-5",
                "data-placeholder": _("輸入一個訂單編號"),
                "data-html": True,
                "data-allow-clear": "false",
            },
        ),
        queryset=Order.objects.none(),
    )

    od_prod = django_filters.ModelChoiceFilter(
        field_name="prod",
        label="品名 / 品號",
        method="orderprod_prod_filter",
        widget=autocomplete.ModelSelect2(
            url="prod_autocomplete",
            attrs={
                "data-theme": "bootstrap-5",
                "data-placeholder": _("輸入一個商品編號或是商品名稱"),
                "data-html": True,
                "data-allow-clear": "false",
            },
        ),
        queryset=Prod.objects.all(),
    )

    od_mfr_id = django_filters.ModelChoiceFilter(
        label="10碼廠編 / 廠商名稱",
        widget=autocomplete.ModelSelect2(
            url="mfr_autocomplete",
            attrs={
                "data-theme": "bootstrap-5",
                "data-placeholder": _("輸入一個廠商編號或是廠商名稱"),
                "data-html": True,
                "data-allow-clear": "false",
            },
        ),
        queryset=Manufacturer.objects.all(),
    )

    od_mfr_id__mfr_user_id = django_filters.ModelChoiceFilter(
        label="訂貨人員",
        widget=autocomplete.ModelSelect2(
            url="mfr_username_autocomplete",
            attrs={
                "data-theme": "bootstrap-5",
                "data-placeholder": _("訂貨人員名稱或是訂貨人員 ID"),
                "data-html": True,
                "data-allow-clear": "false",
            },
        ),
        queryset=get_user_model().objects.all(),
    )

    od_date = django_filters.DateFromToRangeFilter(label="訂貨日期")
    od_except_arrival_date = django_filters.DateFromToRangeFilter(label="預期到貨日")

    class Meta:
        model = Order
        fields = []


class OrderRulesFilter(django_filters.FilterSet):
    def order_rules_prod_filter(self, queryset, name, value):
        prod_rules = queryset.filter(or_type=OrderRuleTypeChoices.Product)
        return prod_rules.filter(or_prod_no=value.prod_no)

    def order_rules_mfr_filter(self, queryset, name, value):
        mfr_rules = queryset.filter(or_type=OrderRuleTypeChoices.Manufacturer)
        mfrs = mfr_rules.filter(or_mfr_id=value.pk)

        prod_rules = queryset.filter(or_type=OrderRuleTypeChoices.Product)
        prods = prod_rules.filter(or_prod_no__prod_mfr_id=value.pk)

        return mfrs | prods

    def order_rules_username_filter(self, queryset, name, value):
        mfr_rules = queryset.filter(or_type=OrderRuleTypeChoices.Manufacturer)
        prod_rules = queryset.filter(or_type=OrderRuleTypeChoices.Product)

        mfrs = mfr_rules.filter(or_mfr_id__mfr_user_id=value.pk)
        prods = prod_rules.filter(or_prod_no__prod_mfr_id__mfr_user_id=value.pk)

        return mfrs | prods

    def order_rules_prod_cate_filter(self, queryset, name, value):
        cates = list(filter(lambda x: x.endswith("cate"), self.form.changed_data))
        cates.sort()
        if cates[-1] != name:
            return queryset

        cates = queryset.filter(or_type=OrderRuleTypeChoices.ProductCategory)
        if name == "or_prod_cate":
            cates = cates.filter(or_prod_cate_no__cate_cate_no=value.pk)
        elif name == "or_prod_subcate":
            cates = cates.filter(or_prod_cate_no__cate_subcate_no=value.pk)
        elif name == "or_prod_subsubcate":
            cates = cates.filter(or_prod_cate_no__cate_no=value.pk)

        return cates

    or_prod_cate = django_filters.ModelChoiceFilter(
        field_name="or_prod_cate",
        label="大分類",
        method="order_rules_prod_cate_filter",
        widget=autocomplete.ModelSelect2(
            url="prod_cate_autocomplete",
            attrs={
                # "data-theme": "bootstrap-5",
                "data-placeholder": _("商品大分類編號或是分類名稱"),
            },
        ),
        queryset=ProdCategory.objects.all(),
    )

    or_prod_subcate = django_filters.ModelChoiceFilter(
        field_name="or_prod_subcate",
        label="中分類",
        method="order_rules_prod_cate_filter",
        widget=autocomplete.ModelSelect2(
            url="prod_subcate_autocomplete",
            forward=["or_prod_cate"],
            attrs={
                # "data-theme": "bootstrap-5",
                "data-placeholder": _("商品中分類編號或是分類名稱"),
            },
        ),
        queryset=ProdCategory.objects.all(),
    )

    or_prod_subsubcate = django_filters.ModelChoiceFilter(
        field_name="or_prod_subsubcate",
        label="小分類",
        method="order_rules_prod_cate_filter",
        widget=autocomplete.ModelSelect2(
            url="prod_subsubcate_autocomplete",
            forward=["or_prod_subcate"],
            attrs={
                # "data-theme": "bootstrap-5",
                "data-placeholder": _("商品小分類編號或是分類名稱"),
            },
        ),
        queryset=ProdCategory.objects.all(),
    )

    or_prod = django_filters.ModelChoiceFilter(
        field_name="prod",
        label="品名 / 品號",
        method="order_rules_prod_filter",
        widget=autocomplete.ModelSelect2(
            url="prod_autocomplete",
            attrs={
                # "data-theme": "bootstrap-5",
                "data-placeholder": _("輸入一個廠商編號或是廠商名稱"),
                "data-html": True,
            },
        ),
        queryset=Prod.objects.all(),
    )

    or_mfr = django_filters.ModelChoiceFilter(
        label="10碼廠編 / 廠商名稱",
        lookup_expr="icontains",
        method="order_rules_mfr_filter",
        widget=autocomplete.ModelSelect2(
            url="mfr_autocomplete",
            attrs={
                # "data-theme": "bootstrap-5",
                "data-placeholder": _("輸入一個廠商編號或是廠商名稱"),
                "data-html": True,
            },
        ),
        queryset=Manufacturer.objects.all(),
    )

    mfr_username = django_filters.ModelChoiceFilter(
        label="訂貨人員",
        lookup_expr="icontains",
        method="order_rules_username_filter",
        widget=autocomplete.ModelSelect2(
            url="mfr_username_autocomplete",
            attrs={
                # "data-theme": "bootstrap-5",
                "data-placeholder": _("訂貨人員名稱或是訂貨人員 ID"),
                "data-html": True,
            },
        ),
        queryset=get_user_model().objects.all(),
    )

    class Meta:
        model = OrderRule
        fields = []


class OrderCirculatedOrderFilter(django_filters.FilterSet):
    mfr_user_id = django_filters.ModelChoiceFilter(
        label="訂貨人員",
        empty_label=None,
        # widget=autocomplete.ModelSelect2(
        #     url="username_autocomplete",
        #     attrs={
        #         "data-placeholder": _("輸入訂貨人員名稱"),
        #     },
        # ),
        queryset=get_user_model().objects.filter(manufacturer__isnull=False).distinct(),
    )

    class Meta:
        model = Manufacturer
        fields = []

    # def get_mfrs(self, request):
    #     if request is None:
    #         return Manufacturer.objects.none()
    #     u = request.user
    #     if "mfr_user_id" in request.GET:
    #         u = request.GET["mfr_user_id"]
    #     mfrs = Manufacturer.objects.filter(mfr_user_id=u)
    #     return mfrs

    # def __init__(self, request, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.filters["mfr_name"].queryset = self.get_mfrs(request)
