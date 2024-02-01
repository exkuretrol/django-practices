from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, FormMixin, UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from manufacturer.models import Manufacturer

from .filters import ProdFilter, ProdNoFilter
from .forms import (
    ExcelTableCreateForm,
    ExcelTableUpdateForm,
    ProdCreateForm,
    ProdUpdateForm,
)
from .models import Prod
from .tables import ProdTable


class ProdDetailView(LoginRequiredMixin, DetailView):
    model = Prod
    context_object_name = "prod"
    template_name = "prod_detail.html"


class ProdListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    paginate_by = 10
    filterset_class = ProdFilter
    table_class = ProdTable
    template_name = "prod_list.html"


class ProdCreateView(LoginRequiredMixin, CreateView):
    model = Prod
    template_name = "prod_create.html"
    form_class = ProdCreateForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super(CreateView, self).get_form_kwargs()
        user = self.request.user
        if user.is_superuser:
            kwargs["mfrs"] = Manufacturer.objects.all()
        else:
            kwargs["mfrs"] = user.manufacturer_set.all()
        return kwargs


class ProdUpdateView(LoginRequiredMixin, UpdateView):
    model = Prod
    form_class = ProdUpdateForm
    template_name = "prod_update.html"


class ProdDeleteView(LoginRequiredMixin, DeleteView):
    model = Prod
    template_name = "prod_delete.html"
    context_object_name = "prod"
    success_url = reverse_lazy("prod_list")


class ProdCreateMultipleView(FormMixin, TemplateView):
    form_class = ExcelTableCreateForm
    template_name = "prod_create_multiple.html"


class ProdUpdateMultipleView(SingleTableMixin, FormMixin, FilterView):
    paginate_by = 10
    template_name = "prod_update_multiple.html"
    filterset_class = ProdNoFilter
    table_class = ProdTable
    form_class = ExcelTableUpdateForm
