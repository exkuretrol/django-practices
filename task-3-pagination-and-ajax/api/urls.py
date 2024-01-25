from django.urls import path
from django.views.generic import TemplateView
from .views import get_data

urlpatterns = [
    path("goods/ajax_get_category/9x9shop", get_data,name="ajax_get_category"),
    path("ajax/", TemplateView.as_view(template_name="prod_ajax.html"), name="ajax_test")
]
