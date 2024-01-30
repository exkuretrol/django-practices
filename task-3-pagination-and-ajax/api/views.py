from django.http import JsonResponse, HttpRequest
from django.db.utils import IntegrityError
from prod.models import Prod
import json


# class ProdListView(LoginRequiredMixin, FormMixin, ListView):
#     paginate_by = 10
#     model = Prod
#     context_object_name = "prods"
#     template_name = "prod_ajax.html"
#     form_class = QueryForm

#     def get(self, request, *args, **kwargs):
#         query = request.GET.get("query", "")

#         form = QueryForm({"query": query})
#         new_form = QueryForm()
#         new_form.fields["query"].widget.attrs.update({"value": query})

#         if form.is_valid():
#             self.object_list = self.get_queryset()
#             context = self.get_context_data()

#             context["form"] = new_form
#             return self.render_to_response(context)
#         else:
#             self.object_list = super().get_queryset()
#             return self.form_invalid(form)

#     def get_queryset(self):
#         query_str = self.request.GET.get("query")
#         if query_str is not None and len(query_str) != 0:
#             prods_list = Prod.objects.filter(prod_query(query_str))
#             return prods_list

#         return super().get_queryset()



    
def create_prods(request: HttpRequest):
    prods_str = request.POST.get("prods", "")
    prods_json = json.loads(prods_str)
    for prod_obj in prods_json:
        try:
            prod = Prod.objects.create(**prod_obj)
            prod.save()
        except IntegrityError as e:
            return JsonResponse({"message": "error while adding new product."})
    return JsonResponse({"message": "success"})

