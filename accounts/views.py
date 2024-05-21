from typing import Any

from constance import config, settings
from constance.admin import ConstanceForm
from constance.utils import get_values
from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, FormView, TemplateView

from .forms import CustomUserAuthenticationForm, CustomUserCreationForm
from .models import CustomUser


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


class CustomLoginView(LoginView):
    form_class = CustomUserAuthenticationForm


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts_profile.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context = self.get_context_data(**kwargs)
        context["mfrs"] = request.user.manufacturer_set.all()
        return self.render_to_response(context)


class UsernameAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = CustomUser.objects.all().order_by("username")
        if self.q:
            qs = qs.filter(username__icontains=self.q)
        return qs


class ConfigView(FormView):
    form_class = ConstanceForm
    template_name = "config.html"
    success_url = reverse_lazy("config")

    def get_initial(self):
        return get_values()

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_config_value(self, name, options, form, initial):
        from datetime import date, datetime

        from django import forms
        from django.utils.formats import localize

        default, help_text = options[0], options[1]
        field_type = None
        if len(options) == 3:
            field_type = options[2]
        # First try to load the value from the actual backend
        value = initial.get(name)
        # Then if the returned value is None, get the default
        if value is None:
            value = getattr(config, name)

        form_field = form[name]
        config_value = {
            "name": name,
            "default": localize(default),
            "raw_default": default,
            "help_text": _(help_text),
            "value": localize(value),
            "modified": localize(value) != localize(default),
            "form_field": form_field,
            "is_date": isinstance(default, date),
            "is_datetime": isinstance(default, datetime),
            "is_checkbox": isinstance(form_field.field.widget, forms.CheckboxInput),
            "is_file": isinstance(form_field.field.widget, forms.FileInput),
        }
        if field_type and field_type in settings.ADDITIONAL_FIELDS:
            serialized_default = form[name].field.prepare_value(default)
            config_value["default"] = serialized_default
            config_value["raw_default"] = serialized_default
            config_value["value"] = form[name].field.prepare_value(value)

        return config_value

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["fieldsets"] = []
        fieldset_items = settings.CONFIG_FIELDSETS.items()
        for fieldset_title, fieldset_data in fieldset_items:
            fields_list = fieldset_data
            collapse = False

            config_values = []
            form = self.get_form()
            initial = self.get_initial()
            for name in fields_list:
                options = settings.CONFIG.get(name)
                if options:
                    config_values.append(
                        self.get_config_value(name, options, form, initial)
                    )

            fieldset_context = {"title": fieldset_title, "config_values": config_values}

            if collapse:
                fieldset_context["collapse"] = True
            context["fieldsets"].append(fieldset_context)
        context["icon_type"] = "gif"
        return context
