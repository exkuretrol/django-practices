import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Prod


class ImageColumn(tables.Column):
    def render(self, value):
        return format_html(f"<img src='{value.url}' width='100' height=auto />")


class DescColumn(tables.Column):
    def render(self, value):
        return f"{value[:20]}..."


class ProdTable(tables.Table):
    prod_img = ImageColumn()
    prod_desc = DescColumn()

    class Meta:
        model = Prod
        row_attrs = {"data-id": lambda record: record.pk}
