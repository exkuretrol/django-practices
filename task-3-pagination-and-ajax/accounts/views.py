from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomUserAuthenticationForm
from django.contrib.auth.views import LoginView


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

class CustomLoginView(LoginView):
    form_class = CustomUserAuthenticationForm
