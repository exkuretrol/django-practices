from django import forms


class ExcelTableForm(forms.Form):
    table_template = f"""prod_no\tprod_name\tprod_desc\tprod_type\tprod_img\tprod_quantity\tprod_status
2501\tAndrew Fields\tCandidate carry student not.\tt1\t/images/300_fzfQXUx.jpeg\t10\tAC
2502\tAndrew Fields\tCandidate carry student not.\tt2\t/images/300_fzfQXUx.jpeg\t20\tIA
2503\tAndrew Fields\tCandidate carry student not.\tt3\t/images/300_fzfQXUx.jpeg\t30\tAC
...
    """
    excel_table = forms.CharField(
        label="Product Create Table",
        required=True,
        widget=forms.Textarea(attrs={"class": "input-form", "placeholder": table_template}),
    )
