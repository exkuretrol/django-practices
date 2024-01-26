from typing import Any
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from prod.forms import QueryForm
from prod.models import Prod
from prod.utils import prod_query


class ProdListView(LoginRequiredMixin, FormMixin, ListView):
    paginate_by = 10
    model = Prod
    context_object_name = "prods"
    template_name = "prod_ajax.html"
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


def get_data(request):
    return JsonResponse({"message": "hello"})


def get_prods(request: HttpRequest):
    query_str = request.GET.get("query", "")
    object_list = Prod.objects.all()
    if query_str is not "":
        data = list(object_list.filter(prod_query(query_str)).values())
    else:
        data = list(object_list.values())

    return JsonResponse({"data": data})
