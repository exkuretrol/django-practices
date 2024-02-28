from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .filters import OrderFilter
from .tables import OrderTable


class OrderList(SingleTableMixin, FilterView):
    table_class = OrderTable
    filterset_class = OrderFilter
    template_name = "order_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["filter"].form
        form.helper = FormHelper()
        form.helper.add_input(Submit("submit", "篩選", css_class="btn btn-primary"))
        form.helper.form_class = "row row-cols-4"
        form.helper.form_method = "get"
        form.helper.form_id = "order-filter-form"

        return context
