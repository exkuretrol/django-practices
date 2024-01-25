from django.http import JsonResponse
from prod.models import Prod
from prod.utils import prod_query

def get_data(request):
    object_list = Prod.objects.all()
    data = list(object_list.filter(prod_query("type:t1")).values())
    return JsonResponse({"data": data})
