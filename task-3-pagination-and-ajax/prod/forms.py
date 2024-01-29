from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.forms.widgets import ClearableFileInput
from .models import Prod
from re import findall


# what if
# "name:david type"
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


class ProdCommonInfo(forms.ModelForm):
    class Meta:
        model = Prod
        fields = "__all__"
        widgets = {
            "prod_name": forms.TextInput(attrs={"class": "input-normal"}),
            "prod_desc": forms.Textarea(attrs={"class": "input-form"}),
            "prod_type": forms.Select(attrs={"class": "input-normal"}),
            "prod_img": forms.FileInput(attrs={"class": "input-file"}),
            "prod_quantity": forms.TextInput(attrs={"class": "input-normal"}),
            "prod_status": forms.Select(attrs={"class": "input-normal"}),
        }
        labels = {
            "prod_name": "Name",
            "prod_desc": "Description",
            "prod_type": "Type",
            "prod_img": "Image",
            "prod_quantity": "Quantity",
            "prod_status": "Status",
        }


class ProdCreateForm(forms.ModelForm):
    class Meta(ProdCommonInfo.Meta):
        pass


class CustomFileInput(ClearableFileInput):
    template_name = "custom_file_input.html"


class ProdUpdateForm(ProdCreateForm):
    class Meta(ProdCommonInfo.Meta):
        widgets = ProdCommonInfo.Meta.widgets
        widgets["prod_img"] = CustomFileInput(attrs={"class": "input-file"})
        pass
