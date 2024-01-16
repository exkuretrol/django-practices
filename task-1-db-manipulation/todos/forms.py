from django import forms
from .models import Todo

class TodoEditForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = (
            "task",
            "completed"
        )
        widgets = {
            "task": forms.TextInput({"class": "text-4xl"}),
        }
