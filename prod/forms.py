from re import findall
from typing import Any, Mapping

from dal import autocomplete
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _

from .models import Prod, ProdRestriction


def validate_query_str(query: str) -> None:
    colon_num = len(findall(":", query))
    res = findall(pattern=r"(name:|desc:|type:|status:)[a-zA-Z0-9]+", string=query)
    if len(res) is not colon_num:
        raise ValidationError(
            "Invalid format. The query string after the colon should only contain alphanumeric characters or numbers."
        )


class QueryForm(forms.Form):
    query = forms.CharField(
        label="query string",
        label_suffix="",
        max_length=255,
        widget=forms.TextInput,
        validators=[
            RegexValidator(
                regex=r"(name:|desc:|type:|status:)",
                message="Invalid format. It should start with 'name:', 'desc:', 'type:', or 'status:'. Do not place a space after the colon.",
            ),
            validate_query_str,
        ],
        required=False,
    )


class CustomFileInput(ClearableFileInput):
    template_name = "base_inputs/file_input.html"


class ProdCommonInfo(forms.ModelForm):
    class Meta:
        model = Prod
        fields = "__all__"
        widgets = {
            "prod_desc": forms.Textarea(attrs={"rows": 5}),
            "prod_img": CustomFileInput,
            "prod_cate_no": autocomplete.ModelSelect2(
                url="prod_all_cate_autocomplete",
                attrs={
                    "data-placeholder": _("輸入一個商品分類編號或是商品名稱"),
                },
            ),
            "prod_mfr_id": autocomplete.ListSelect2(
                url="mfr_autocomplete",
                attrs={
                    "data-placeholder": _("輸入一個廠商編號或是廠商名稱"),
                },
            ),
        }


class ProdCreateForm(forms.ModelForm):
    def __init__(self, mfrs, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        choices_list = [(mfr.pk, mfr.mfr_name) for mfr in mfrs]
        self.fields["prod_mfr_id"].choices = choices_list

    class Meta(ProdCommonInfo.Meta):
        pass


class ProdUpdateForm(ProdCreateForm):
    class Meta(ProdCommonInfo.Meta):
        pass


class ExcelTableCreateForm(forms.Form):
    table_template = f"""prod_no\tprod_name\tprod_desc\tprod_img\tprod_quantity\tprod_cate_no\tprod_sales_status\tprod_quality_assurance_status\tprod_mfr_id
855175\tAndrew Fields\tCandidate carry student not.\t/images/300_fzfQXUx.jpeg\t10\t000001\t0\t0\t1
855176\tAndrew Fields\tCandidate carry student not.\t/images/300_fzfQXUx.jpeg\t10\t000001\t0\t0\t1
855177\tAndrew Fields\tCandidate carry student not.\t/images/300_fzfQXUx.jpeg\t10\t000001\t0\t0\t1"""
    excel_table = forms.CharField(
        label="Product Create Table",
        required=True,
        widget=forms.Textarea(
            attrs={"class": "input-form", "placeholder": table_template}
        ),
    )


class ExcelTableUpdateForm(forms.Form):
    table_template = f"""prod_no	prod_quantity
855175	10
855176	20
855177	30"""
    excel_table = forms.CharField(
        label="Product Update Table",
        required=True,
        widget=forms.Textarea(
            attrs={"class": "input-form", "placeholder": table_template}
        ),
    )


class ProdRestrictionCreateForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = ProdRestriction
        widgets = {
            "pr_prod_no": autocomplete.ModelSelect2(url="prod_autocomplete"),
        }
