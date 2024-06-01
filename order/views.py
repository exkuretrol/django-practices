import re
from typing import List

from constance import config
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Submit
from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Case, QuerySet, When
from django.db.models.query import QuerySet
from django.forms import modelformset_factory
from django.forms.models import BaseModelFormSet
from django.http import QueryDict
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.datastructures import MultiValueDict
from django.utils.translation import gettext as _
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import CreateView, FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from accounts.models import CustomUser
from manufacturer.models import Manufacturer
from prod.models import Prod

from .filters import OrderCirculatedOrderFilter, OrderFilter, OrderRulesFilter
from .forms import (
    CirculatedOrderManufacturerForm,
    OrderBeforeCreateForm,
    OrderCreateForm,
    OrderFormset,
    OrderProdCreateForm,
    OrderProdCreateFormset,
    OrderProdUpdateFormset,
    OrderUpdateForm,
    get_order_no_from_day,
)
from .models import Order, OrderProd
from .tables import CirculatedOrderTable, OrderRulesTable, OrderTable


class OrderListView(SingleTableMixin, FilterView):
    table_class = OrderTable
    filterset_class = OrderFilter
    template_name = "order_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header_title"] = _("訂貨查詢維護")
        context["header_description"] = _("查詢訂貨資料，並進行維護。")
        form = context["filter"].form
        form.helper = FormHelper()
        form.helper.add_input(Submit("submit", "篩選", css_class="btn btn-primary"))
        form.helper.add_input(
            Button(
                "clear", "清除", css_class="btn btn-secondary", onclick="clearFilter()"
            )
        )
        form.helper.form_class = "row row-cols-4"
        form.helper.form_method = "get"
        form.helper.form_id = "order-filter-form"

        return context


class OrderProdInline:
    form_class = OrderUpdateForm
    model = Order
    template_name = "order_update.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((_.is_valid() for _ in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))
        self.object = form.save()
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, f"formset_{name}_valid", None)

            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()

        return redirect(to="order_list")

    def formset_orderprod_valid(self, formset):
        prods = formset.save(commit=False)
        for prod in formset.deleted_objects:
            prod.delete()
        for prod in prods:
            prod.save()


class OrderUpdateView(OrderProdInline, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["named_formset"] = self.get_named_formsets()
        return context

    def get_named_formsets(self):
        return {
            "orderprod": OrderProdUpdateFormset(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="orderprod",
            )
        }


class OrderBeforeCreateView(FormView):
    form_class = OrderBeforeCreateForm
    template_name = "order_create_clipboard_before_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header_title"] = _("零散訂貨作業")
        context["header_description"] = _("按貼上按鈕貼上訂貨資料，然後按下一步。")
        form = context["form"]
        form.helper = FormHelper()
        form.helper.add_input(
            Submit("submit", _("下一步"), css_class="btn btn-primary")
        )
        return context

    def get_success_url(self) -> str:
        return reverse_lazy("order_create_multiple")

    def form_valid(self, form):
        clipboard = form.cleaned_data["clipboard"]
        self.request.session["clipboard"] = clipboard
        return super().form_valid(form)


class OrderCreateView(FormView):
    template_name = "order_create.html"
    form_class = OrderCreateForm


class OrderCreateMultipleView(CreateView):
    template_name = "order_create_multiple.html"
    form_class = OrderCreateForm
    model = Order

    def get_success_url(self) -> str:
        return reverse_lazy("order_create_clipboard")

    def get_named_formset(self):
        clipboard = self.request.session.pop("clipboard", None)
        OrderDynamicFormset = modelformset_factory(
            Order, OrderCreateForm, extra=len(clipboard.items())
        )
        initial = []
        prods_formset_list = []

        for i, (mfr_id, prods) in enumerate(clipboard.items()):
            OrderProdDynamicFormset = modelformset_factory(
                OrderProd, OrderProdCreateForm, extra=len(prods), can_delete=True
            )
            od_no = get_order_no_from_day() + i + 1
            mfr = Manufacturer.objects.get(mfr_id=mfr_id)
            initial.append(
                {
                    "od_no": od_no,
                    "od_mfr_id": mfr.pk,
                    "od_mfr_name": mfr.mfr_name,
                    "od_mfr_full_id": mfr.mfr_full_id,
                    "od_mfr_user_id_username": mfr.mfr_user_id.username,
                }
            )

            prods_formset_list.append(
                OrderProdDynamicFormset(
                    initial=[
                        {
                            "op_prod": Prod.objects.get(
                                pk=int(prod["prod_no"])
                            ).prod_name,
                            "op_prod_no": prod["prod_no"],
                            "op_quantity": prod["quantity"],
                            "op_od_no": od_no,
                        }
                        for prod in prods
                    ],
                    queryset=OrderProd.objects.none(),
                    prefix=f"orderprod_{i}",
                )
            )
        return {
            "order_formset": OrderDynamicFormset(
                initial=initial,
                queryset=Order.objects.none(),
                prefix="order",
            ),
            "prods_formset_list": prods_formset_list,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.pop("form")
        if self.request.method == "GET":
            context["named_formset"] = self.get_named_formset()
        return context

    def form_valid(
        self,
        order_formset: BaseModelFormSet,
        orderprod_formset_list: List[BaseModelFormSet],
    ):
        # TODO: orders create after all orderprods are valid
        orders = order_formset.save(commit=False)
        for order in orders:
            order.save()
        if not all((_.is_valid() for _ in orderprod_formset_list)):
            for order in orders:
                order.delete()
            return self.render_to_response(
                self.get_context_data(
                    named_formset={
                        "order_formset": order_formset,
                        "prods_formset_list": orderprod_formset_list,
                    }
                )
            )

        for orderprod in orderprod_formset_list:
            self.formset_orderprod_valid(orderprod)

        return redirect("order_create_clipboard")

    def form_invalid(self, order_formset, orderprod_formset_list):
        print(order_formset.errors)
        for orderprod_formset in orderprod_formset_list:
            print(orderprod_formset.errors)
        return self.render_to_response(
            self.get_context_data(
                named_formset={
                    "order_formset": order_formset,
                    "prods_formset_list": orderprod_formset_list,
                }
            )
        )

    def formset_orderprod_valid(self, formset):
        prods = formset.save(commit=False)
        for prod in prods:
            prod.save()

    def get(self, request, *args, **kwargs):
        if request.session.get("clipboard", None) is None:
            return redirect("order_create_clipboard")

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        order_formset = OrderFormset(data=self.request.POST, prefix="order")

        orderprod_formset_list = []
        orderprod_prefix = set(
            [
                "orderprod_" + re.search(r"\d+", k).group()
                for k in request.POST.keys()
                if k.startswith("orderprod")
            ]
        )
        for prefix in orderprod_prefix:
            orderprod_formset_list.append(
                OrderProdCreateFormset(data=self.request.POST, prefix=prefix)
            )

        if order_formset.is_valid():
            return self.form_valid(order_formset, orderprod_formset_list)
        else:
            return self.form_invalid(order_formset, orderprod_formset_list)


class OrderRulesView(SingleTableMixin, FilterView):
    filterset_class = OrderRulesFilter
    table_class = OrderRulesTable
    template_name = "order_rules.html"


class OrderNoAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 100

    def get_queryset(self):
        qs = Order.objects.all()
        if self.q:
            qs = qs.filter(od_no__startswith=self.q)
        return qs.order_by("-od_no")


class OrderCirculatedOrderView(
    LoginRequiredMixin, SingleTableMixin, FilterView, FormView
):
    form_class = CirculatedOrderManufacturerForm
    filterset_class = OrderCirculatedOrderFilter
    template_name = "order_circulated_order.html"
    table_class = CirculatedOrderTable
    paginate_by = 1
    page_kwarg = "mfr_page"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        u = self.request.user
        if "mfr_user_id" in self.request.GET:
            u = self.request.GET["mfr_user_id"]
        mfrs = Manufacturer.objects.filter(mfr_user_id=u)
        mfrs_options = [(mfr.pk, mfr.mfr_name) for mfr in mfrs]
        kwargs["choices"] = mfrs_options
        if self.page_kwarg in self.request.GET:
            kwargs["initial"] = int(self.request.GET[self.page_kwarg]) - 1
        return kwargs

    def get_table_pagination(self, table):
        paginate = super().get_table_pagination(table)
        paginate["per_page"] = config.CIRCULATED_ORDER_PER_PAGE_ITEMS
        return paginate

    def get_table_data(self):
        mfr_page = int(self.request.GET.get(self.page_kwarg, 1))
        try:
            current_mfr = self.object_list.__getitem__(mfr_page - 1)
            if isinstance(current_mfr, Manufacturer):
                return current_mfr.prod_set.all()
        except:
            pass

        return Prod.objects.none()

    def get_queryset(self):
        u = self.request.user
        if "mfr_user_id" in self.request.GET:
            u = CustomUser.objects.get(pk=self.request.GET["mfr_user_id"])
        return Manufacturer.objects.filter(mfr_user_id=u).order_by("mfr_id")

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        if kwargs["data"]:
            pass
        else:
            qd = QueryDict(mutable=True)
            qd.update({"mfr_user_id": self.request.user.pk})
            kwargs["data"] = qd
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header_title"] = _("每日訂貨作業")
        context["header_description"] = _("查看每日訂貨資料，並進行維護。")
        return context