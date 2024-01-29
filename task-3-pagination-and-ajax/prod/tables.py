import django_tables2 as tables
from .models import Prod

class ProdTable(tables.Table):
    class Meta:
        model = Prod
        row_attrs = {
            "data-id": lambda record: record.pk
        }
        exclude = ["prod_img"]