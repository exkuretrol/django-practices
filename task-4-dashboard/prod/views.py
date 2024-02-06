import datetime
import json
from typing import Any

import django_tables2
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F
from django.db.models.functions import Substr
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, FormMixin, UpdateView
from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, SingleTableMixin
from manufacturer.models import Manufacturer

from .filters import ProdFilter, ProdNoFilter
from .forms import (
    ExcelTableCreateForm,
    ExcelTableUpdateForm,
    ProdCreateForm,
    ProdUpdateForm,
)
from .models import Prod
from .tables import ProdCateTable, ProdMfrTable, ProdTable


class ProdDetailView(LoginRequiredMixin, DetailView):
    model = Prod
    context_object_name = "prod"
    template_name = "prod_detail.html"


class ProdListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    paginate_by = 10
    filterset_class = ProdFilter
    table_class = ProdTable
    template_name = "prod_list.html"


class ProdCreateView(LoginRequiredMixin, CreateView):
    model = Prod
    template_name = "prod_create.html"
    form_class = ProdCreateForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super(CreateView, self).get_form_kwargs()
        user = self.request.user
        if user.is_superuser:
            kwargs["mfrs"] = Manufacturer.objects.all()
        else:
            kwargs["mfrs"] = user.manufacturer_set.all()
        return kwargs


class ProdUpdateView(LoginRequiredMixin, UpdateView):
    model = Prod
    form_class = ProdUpdateForm
    template_name = "prod_update.html"


class ProdDeleteView(LoginRequiredMixin, DeleteView):
    model = Prod
    template_name = "prod_delete.html"
    context_object_name = "prod"
    success_url = reverse_lazy("prod_list")


class ProdCreateMultipleView(FormMixin, TemplateView):
    form_class = ExcelTableCreateForm
    template_name = "prod_create_multiple.html"


class ProdUpdateMultipleView(SingleTableMixin, FormMixin, FilterView):
    paginate_by = 10
    template_name = "prod_update_multiple.html"
    filterset_class = ProdNoFilter
    table_class = ProdTable
    form_class = ExcelTableUpdateForm


def datetimeconverter(o):
    if isinstance(o, datetime.date):
        return o.isoformat()
    elif isinstance(o, datetime.datetime):
        return o.isoformat()


class ProdDashboardView(MultiTableMixin, TemplateView):
    template_name = "prod_dashboard.html"

    user_prods_nums = (
        Prod.objects.all()
        .select_related("prod_mfr_id_id__mfr_user_id_id")
        .annotate(
            user_id=F("prod_mfr_id_id__mfr_user_id_id__id"),
            user_name=F("prod_mfr_id_id__mfr_user_id_id__username"),
        )
        .values("user_id", "user_name")
        .annotate(
            prod_nums=Count("prod_no"),
        )
    )

    user_mfr_nums = (
        Manufacturer.objects.all()
        .values("mfr_user_id")
        .annotate(mfr_main_nums=Count("mfr_main_id"), mfr_sub_nums=Count("mfr_sub_id"))
    )

    dict2 = {d["mfr_user_id"]: d for d in user_mfr_nums}

    out = []
    for d1 in user_prods_nums:
        d = dict(**d1)
        d.update(dict2.get(d1["user_id"], {}))
        d.pop("mfr_user_id")
        out.append(d)

    mfr_cate = (
        Prod.objects.all()
        .select_related("mfr_category_id__mfr_cate_name")
        .select_related("prod_mfr_id_id__mfr_user_id_id")
        .annotate(
            user_id=F("prod_mfr_id_id__mfr_user_id_id__id"),
            user_name=F("prod_mfr_id_id__mfr_user_id_id__username"),
        )
        .values("user_name")
        .annotate(cate=Substr(F("prod_category_id__cate_name"), 1, 3))
        .values("user_name", "cate")
        .annotate(cate_nums=Count("cate"))
    )
    import pandas as pd

    out2 = (
        pd.DataFrame(mfr_cate)
        .pivot(index=["cate"], columns=["user_name"], values="cate_nums")
        .fillna(0)
        .astype(int)
        .reset_index()
        .to_dict(orient="records")
    )

    columns = [(k, django_tables2.Column()) for k in out2[0].keys()]

    t1 = ProdMfrTable(out)
    t2 = ProdCateTable(out2, extra_columns=columns)
    tables = [t1, t2]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["json"] = {}
        return context

    # context["json"] = json.dumps(
    #     out,
    #     default=datetimeconverter,
    # )
