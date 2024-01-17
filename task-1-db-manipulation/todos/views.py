from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views.generic import ListView, CreateView
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Todo
from .forms import TodoEditForm
from django.urls import reverse_lazy


class TodoListView(ListView):
    context_object_name = "todos"
    model = Todo
    template_name = "todo_home.html"

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None
        return Todo.objects.filter(author=self.request.user).order_by("pk")


class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    template_name = "todo_create.html"
    fields = ["task"]
    success_url = reverse_lazy("todolist")
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)


class TodoDeleteView(LoginRequiredMixin, DeleteView):
    context_object_name = "todo_to_delete"
    model = Todo
    template_name = "todo_delete.html"
    success_url = reverse_lazy("todolist")


class TodoUpdateView(LoginRequiredMixin, UpdateView):
    context_object_name = "todo_to_update"
    model = Todo
    template_name = "todo_edit.html"
    success_url = reverse_lazy("todolist")
    form_class = TodoEditForm
