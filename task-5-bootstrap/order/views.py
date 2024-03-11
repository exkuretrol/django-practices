from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Submit
from django.forms import inlineformset_factory, modelformset_factory
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, UpdateView
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
    OrderProdForm,
    OrderProdFormset,
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

    def get_queryset(self):
        return None

    def get_formset(self):
        if self.request.method == "GET":
            clipboard = self.request.session.pop("clipboard", None)
            OrderDynamicFormset = modelformset_factory(
                Order, OrderCreateForm, extra=len(clipboard.items())
            )
            initial = []
            for i, (mfr_id, prods) in enumerate(clipboard.items()):
                initial.append(
                    {
                        "od_no": get_current_order_no() + i + 1,
                        "od_mfr_id": Manufacturer.objects.get(mfr_id=mfr_id),
                        "od_notes": prods,
                    }
                )
            return OrderDynamicFormset(
                initial=initial,
                queryset=Order.objects.none(),
                prefix="order",
            )
        else:
            return OrderFormset(
                data=self.request.POST,
                prefix="order",
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = self.get_formset()
        return context
        # prods_formset = []

        # prods_formset.append(
        #     OrderProdFormset(
        #         initial=[
        #             {
        #                 "op_prod": Prod.objects.get(pk=int(prod["prod_no"])),
        #                 "op_quantity": prod["quantity"],
        #             }
        #             for prod in prods
        #         ],
        #         queryset=OrderProd.objects.none(),
        #         prefix=f"orderprod_{i}",
        #     )
        # )

        # context["forms"] = zip(
        #     OrderFormset(
        #         initial=initial,
        #         queryset=Order.objects.none(),
        #         prefix="order",
        #     ),
        #     prods_formset,
        # )

    def form_valid(self, formset):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()

        return redirect("order_create_clipboard")

    def form_invalid(self, formset):
        for form in formset:
            print(form.errors)
        return super().form_invalid(formset)

    def post(self, request: HttpRequest, *args, **kwargs):
        order_formset = OrderFormset(data=self.request.POST, prefix="order")
        if order_formset.is_valid():
            return self.form_valid(order_formset)
        else:
            return self.form_invalid(order_formset)
