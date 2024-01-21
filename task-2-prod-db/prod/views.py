from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q
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


class ProdSearchView(ListView):
    model = Prod
    context_object_name = "prods"
    template_name = "prod_search_result.html"

    def get_queryset(self) -> QuerySet[Any]:
        query = self.request.GET.get("q")
        print(query)

        def query_by_what(query: str):
            conds = query.split(" ")
            filters = None
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

        prods_list = Prod.objects.filter(query_by_what(query))
        return prods_list


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
