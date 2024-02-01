from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import CustomUserAuthenticationForm, CustomUserCreationForm


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
