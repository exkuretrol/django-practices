import re
from typing import List

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Submit
from django.forms import modelformset_factory
from django.forms.models import BaseModelFormSet
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import UpdateView
from django.views.generic.edit import CreateView, FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from manufacturer.models import Manufacturer
from prod.models import Prod

from .filters import OrderFilter
from .forms import (
    OrderBeforeCreateForm,
    OrderCreateForm,
    OrderFormset,
    OrderProdCreateForm,
    OrderProdCreateFormset,
    OrderProdUpdateFormset,
    OrderUpdateForm,
    get_current_order_no,
)
from .models import Order, OrderProd
from .tables import OrderTable


class OrderListView(SingleTableMixin, FilterView):
    table_class = OrderTable
    filterset_class = OrderFilter
    template_name = "order_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        form = context["form"]
        form.helper = FormHelper()
        form.helper.add_input(Submit("submit", "篩選", css_class="btn btn-primary"))
        form.helper.form_class = "row row-cols-4"
        form.helper.form_method = "post"
        form.helper.form_id = "order-update-form"

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
            od_no = get_current_order_no() + i + 1
            initial.append(
                {
                    "od_no": od_no,
                    "od_mfr_id": Manufacturer.objects.get(mfr_id=mfr_id),
                    "od_notes": prods,
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
        orders = order_formset.save(commit=False)
        for order in orders:
            order.save()
        if not all((_.is_valid() for _ in orderprod_formset_list)):
            # TODO: remove orders when orderprod_formset_list is invalid
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
        for prod in formset.deleted_objects:
            prod.delete()

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
