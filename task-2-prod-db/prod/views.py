from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Prod
from django.urls import reverse_lazy


class ProdDetailView(DetailView):
    model = Prod
    context_object_name = "prod"
    template_name = "prod_detail.html"


class ProdListView(ListView):
    model = Prod
    context_object_name = "prods"
    template_name = "prod_list.html"


class ProdCreateView(CreateView):
    model = Prod
    template_name = "prod_create.html"
    fields = [
        "prod_name",
        "prod_desc",
        "prod_img",
        "prod_type",
        "prod_quantity",
        "prod_status",
    ]


class ProdUpdateView(UpdateView):
    model = Prod
    fields = [
        "prod_name",
        "prod_desc",
        "prod_img",
        "prod_type",
        "prod_quantity",
        "prod_status",
    ]
    template_name = "prod_update.html"


class ProdDeleteView(DeleteView):
    model = Prod
    template_name = "prod_delete.html"
    context_object_name = "prod"
    success_url = reverse_lazy("prod_list")
