from typing import Any
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from prod.forms import QueryForm
from prod.models import Prod
from prod.utils import prod_query


class ProdListView(LoginRequiredMixin, FormMixin, ListView):
    model = Prod
    form_class = QueryForm
    template_name = "prod_ajax.html"
    context_object_name = "prods"
    # def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    #     return super().get(request, *args, **kwargs)


def get_data(request):
    return JsonResponse({"message": "hello"})


def get_prods(request: HttpRequest):
    query_str = request.GET.get("query", "")
    object_list = Prod.objects.all()
    data = list(object_list.filter(prod_query(query_str)).values())
    return JsonResponse({"data": data})
