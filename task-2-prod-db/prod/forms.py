from django import forms
from django.core.validators import RegexValidator
class QueryForm(forms.Form):
    query = forms.CharField(
        label="query string", 
        label_suffix="", 
        max_length=255, 
        widget=forms.TextInput,
        validators=[
            RegexValidator(
                regex=r'(name:|desc:|type:|status:)',
                message="Invalid query format. It should start with name: / desc: / type: / status: .",
            ),
        ],
    )
