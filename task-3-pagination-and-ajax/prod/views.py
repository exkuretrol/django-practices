from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Prod
from django.urls import reverse_lazy
from .forms import QueryForm, ProdCreateForm, ProdUpdateForm
from .utils import prod_query


class ProdDetailView(LoginRequiredMixin, DetailView):
    model = Prod
    context_object_name = "prod"
    template_name = "prod_detail.html"


class ProdListView(LoginRequiredMixin, FormMixin, ListView):
    paginate_by = 10
    model = Prod
    context_object_name = "prods"
    template_name = "prod_list.html"
    form_class = QueryForm

    def get(self, request, *args, **kwargs):
        query = request.GET.get("query", "")

        form = QueryForm({"query": query})
        new_form = QueryForm()
        new_form.fields["query"].widget.attrs.update({"value": query})

        if form.is_valid():
            self.object_list = self.get_queryset()
            context = self.get_context_data()

            context["form"] = new_form
            return self.render_to_response(context)
        else:
            self.object_list = super().get_queryset()
            return self.form_invalid(form)

    def get_queryset(self):
        query_str = self.request.GET.get("query")
        if query_str is not None and len(query_str) != 0:
            prods_list = Prod.objects.filter(prod_query(query_str))
            return prods_list

        return super().get_queryset()


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
