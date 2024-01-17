from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Todo


class TodoEditForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ("task", "completed")
