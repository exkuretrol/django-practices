from django.views.generic import ListView
from django.views.generic.edit import CreateView
from .models import Prod


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
