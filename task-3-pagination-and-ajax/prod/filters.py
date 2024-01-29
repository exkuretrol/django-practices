import django_filters as filters
from .models import Prod

class ProdFilter(filters.FilterSet):
    class Meta:
        model = Prod
        fields = ["prod_name", "prod_desc", "prod_type", "prod_status"]
