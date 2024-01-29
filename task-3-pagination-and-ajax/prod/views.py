from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Prod
from django.urls import reverse_lazy
from .forms import ProdCreateForm, ProdUpdateForm
from .tables import ProdTable
from .filters import ProdFilter
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView


class ProdDetailView(LoginRequiredMixin, DetailView):
    model = Prod
    context_object_name = "prod"
    template_name = "prod_detail.html"


class ProdListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    paginate_by = 10
    filterset_class = ProdFilter
    table_class = ProdTable
    context_object_name = "prods"
    template_name = "prod_list.html"


class ProdCreateView(LoginRequiredMixin, CreateView):
    model = Prod
    template_name = "prod_create.html"
    form_class = ProdCreateForm


class ProdUpdateView(LoginRequiredMixin, UpdateView):
    model = Prod
    form_class = ProdUpdateForm
    template_name = "prod_update.html"


class ProdDeleteView(LoginRequiredMixin, DeleteView):
    model = Prod
    template_name = "prod_delete.html"
    context_object_name = "prod"
    success_url = reverse_lazy("prod_list")
