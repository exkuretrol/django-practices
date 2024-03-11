from re import findall
from typing import Any, Mapping

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.core.validators import RegexValidator
from django.db.models.base import Model
from django.forms.utils import ErrorList
from django.forms.widgets import ClearableFileInput

from .models import Prod


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
    template_name = "custom_file_input.html"


class ProdCommonInfo(forms.ModelForm):
    class Meta:
        model = Prod
        fields = "__all__"
        widgets = {
            "prod_desc": forms.Textarea,
            "prod_img": CustomFileInput,
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["prod_img"].required = False
        self.fields["prod_desc"].required = False


class ProdCreateForm(forms.ModelForm):
    def __init__(self, mfrs, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        choices_list = [(mfr.pk, mfr.mfr_name) for mfr in mfrs]
        self.fields["prod_mfr_id"].choices = choices_list

    class Meta(ProdCommonInfo.Meta):
        pass


class ProdUpdateForm(ProdCreateForm):
    class Meta(ProdCommonInfo.Meta):
        widgets = ProdCommonInfo.Meta.widgets
        widgets["prod_img"] = CustomFileInput(attrs={"class": "input-file"})
        pass


class ExcelTableCreateForm(forms.Form):
    table_template = f"""prod_no\tprod_name\tprod_desc\tprod_type\tprod_img\tprod_quantity\tprod_status
2501\tAndrew Fields\tCandidate carry student not.\tt1\t/images/300_fzfQXUx.jpeg\t10\tAC
2502\tAndrew Fields\tCandidate carry student not.\tt2\t/images/300_fzfQXUx.jpeg\t20\tIA
2503\tAndrew Fields\tCandidate carry student not.\tt3\t/images/300_fzfQXUx.jpeg\t30\tAC
...
    """
    excel_table = forms.CharField(
        label="Product Create Table",
        required=True,
        widget=forms.Textarea(
            attrs={"class": "input-form", "placeholder": table_template}
        ),
    )


class ExcelTableUpdateForm(forms.Form):
    table_template = f"""prod_no	prod_quantity
2501	10
2502	20
2503	30
..."""
    excel_table = forms.CharField(
        label="Product Update Table",
        required=True,
        widget=forms.Textarea(
            attrs={"class": "input-form", "placeholder": table_template}
        ),
    )
