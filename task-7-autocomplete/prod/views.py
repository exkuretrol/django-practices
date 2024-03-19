import datetime
from typing import Any

import django_tables2
import pandas as pd
from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q
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
from .models import CateTypeChoices, Prod, ProdCategory
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

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        user = self.request.user
        if user.is_superuser:
            kwargs["mfrs"] = Manufacturer.objects.all()
        else:
            kwargs["mfrs"] = user.manufacturer_set.all()
        return kwargs


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
    pass
    # d3 = {
    #     cate.cate_id: cate.cate_name
    #     for cate in ProdCategory.objects.filter(cate_type=CateTypeChoices.Cate)
    # }
    # def get_cate_name_by_id(cate_id: str):
    #     return d3.get(cate_id, None)
    # template_name = "prod_dashboard.html"

    # user_prods_nums = (
    #     Prod.objects.all()
    #     .select_related("prod_mfr_id_id__mfr_user_id_id")
    #     .annotate(
    #         user_id=F("prod_mfr_id_id__mfr_user_id_id__id"),
    #         user_name=F("prod_mfr_id_id__mfr_user_id_id__username"),
    #     )
    #     .values("user_id", "user_name")
    #     .annotate(
    #         prod_nums=Count("prod_no"),
    #     )
    # )

    # user_mfr_nums = (
    #     Manufacturer.objects.all()
    #     .values("mfr_user_id")
    #     .annotate(mfr_main_nums=Count("mfr_main_id"), mfr_sub_nums=Count("mfr_sub_id"))
    # )

    # out = []
    # if user_prods_nums.exists() and user_mfr_nums.exists():
    #     dict2 = {d["mfr_user_id"]: d for d in user_mfr_nums}

    #     for d1 in user_prods_nums:
    #         d = dict(**d1)
    #         d.update(dict2.get(d1["user_id"], {}))
    #         d.pop("mfr_user_id")
    #         out.append(d)

    #     t1 = ProdMfrTable(out, attrs={"table-name": "prod_mfr", "class": "table"})
    # else:
    #     t1 = ProdMfrTable({}, attrs={"table-name": "prod_mfr", "class": "table"})
    # mfr_cate = (
    #     Prod.objects.all()
    #     .select_related("mfr_category_id__mfr_cate_name")
    #     .select_related("prod_mfr_id_id__mfr_user_id_id")
    #     .annotate(
    #         user_id=F("prod_mfr_id_id__mfr_user_id_id__id"),
    #         user_name=F("prod_mfr_id_id__mfr_user_id_id__username"),
    #     )
    #     .values("user_id", "user_name")
    #     .annotate(cate=F("prod_category_id__main_cate_id"))
    #     .values("user_id", "user_name", "cate")
    #     .annotate(cate_nums=Count("cate"))
    # )
    # if mfr_cate.exists():

    #     out2 = (
    #         pd.DataFrame(mfr_cate)
    #         .pivot(index=["user_id", "user_name"], columns=["cate"], values="cate_nums")
    #         .fillna(0)
    #         .astype(int)
    #         .reset_index()
    #         .to_dict(orient="records")
    #     )

    #     columns = []

    #     class SummingColumn(django_tables2.Column):
    #         def render_footer(self, bound_column, table):
    #             return sum(bound_column.accessor.resolve(row) for row in table.data)

    #     for k in out2[0].keys():
    #         if k in ["user_id", "user_name"]:
    #             continue
    #         columns.append(
    #             (
    #                 k,
    #                 SummingColumn(
    #                     verbose_name=get_cate_name_by_id(k), attrs={"td": {"col": k}}
    #                 ),
    #             )
    #         )

    #     t2 = ProdCateTable(
    #         out2,
    #         extra_columns=columns,
    #         attrs={"table-name": "prod_cate", "class": "table"},
    #     )

    # else:
    #     t2 = ProdCateTable({})

    # tables = [t1, t2]

    # def get_context_data(self, **kwargs) -> dict[str, Any]:
    #     context = super().get_context_data(**kwargs)
    #     context["prod_cate_data"] = self.out
    #     return context


class ProdCategoryAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 100

    def get_queryset(self):
        qs = ProdCategory.objects.all()
        if self.q:
            qs = qs.filter(
                Q(cate_no__icontains=self.q) | Q(cate_name__icontains=self.q)
            )
        return qs


class ManufacturerAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 100

    def get_queryset(self):
        qs = Manufacturer.objects.all()
        if self.q:
            qs = qs.filter(mfr_name__icontains=self.q)

        return qs
