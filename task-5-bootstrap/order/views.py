from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Submit
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.views.generic.edit import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .filters import OrderFilter
from .forms import (
    OrderBeforeCreateForm,
    OrderCreateForm,
    OrderProdFormset,
    OrderUpdateForm,
)
from .models import Order
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
        # for form in formset:
        #     if form.instance.op_quantity <= 0:
        #         form.add_error(
        #             "op_quantity",
        #             "訂貨數量必須大於 0",
        #         )
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
            "orderprod": OrderProdFormset(
                self.request.POST or None,
                self.request.FILES or None,
                instance=self.object,
                prefix="orderprod",
            )
        }


class OrderBeforeCreateView(FormView):
    form_class = OrderBeforeCreateForm
    template_name = "order_create_clipboard_before_create.html"

    def get_success_url(self) -> str:
        self.request.session["clipboard"] = self.request.POST["clipboard"]
        return reverse_lazy("order_create")


class OrderCreateView(FormView):

    form_class = OrderCreateForm
    template_name = "order_create.html"
