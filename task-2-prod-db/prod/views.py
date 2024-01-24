from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Prod
from django.urls import reverse_lazy
from .forms import QueryForm, ProdCreateForm, ProdUpdateForm

class ProdDetailView(LoginRequiredMixin, DetailView):
    model = Prod
    context_object_name = "prod"
    template_name = "prod_detail.html"


class ProdListView(LoginRequiredMixin, FormMixin, ListView):
    model = Prod
    context_object_name = "prods"
    template_name = "prod_list.html"
    form_class = QueryForm

    def get_queryset(self):
        query_str = self.request.POST.get("query")
        if query_str is not None and len(query_str) is not 0:

            def query_by_what(query: str):
                conds = query.split(" ")
                filters = Q()
                for cond in conds:
                    col, value = cond.split(":")
                    if col == "name":
                        filters &= Q(prod_name__contains=value)
                    elif col == "desc":
                        filters &= Q(prod_desc__contains=value)
                    elif col == "type":
                        filters &= Q(prod_type__contains=value)
                    elif col == "status":
                        filters &= Q(prod_status__contains=value)
                return filters

            prods_list = Prod.objects.filter(query_by_what(query_str))
            return prods_list

        return super().get_queryset()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.get(request, *args, **kwargs)
        else:
            self.object_list = super().get_queryset()
            return self.form_invalid(form)


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
