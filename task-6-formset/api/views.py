import json

from django.db.utils import IntegrityError
from django.http import HttpRequest, JsonResponse
from prod.models import Prod


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


def update_prods(request: HttpRequest):
    prods_str = request.POST.get("prods", "")
    prods_json = json.loads(prods_str)
    for prod_obj in prods_json:
        try:
            prod = Prod.objects.get(prod_no=prod_obj["prod_no"])
            prod.prod_quantity = prod_obj["prod_quantity"]
            prod.save()
        except IntegrityError as e:
            return JsonResponse({"message": "error while updating new product."})
    return JsonResponse({"message": "success"})
