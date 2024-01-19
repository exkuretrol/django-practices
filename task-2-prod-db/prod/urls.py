from django.urls import path
from django.views.generic.base import TemplateView
from .views import ProdListView, ProdCreateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("prods/", ProdListView.as_view(), name="prod_list"),
    path("prods/create/", ProdCreateView.as_view(), name="prod_create")
]
