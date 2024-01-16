from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import DeleteView, UpdateView
from .models import Todo
from .forms import TodoEditForm
from django.urls import reverse_lazy

class TodoListView(ListView):
    context_object_name = "todos"
    model = Todo
    template_name = "todo_home.html"

class TodoDetailView(DetailView):
    model = Todo

class TodoCreateView(CreateView):
    model = Todo
    template_name = "todo_create.html"
    fields = ["task", "author"]
    success_url = reverse_lazy("todolist")

class TodoDeleteView(DeleteView):
    context_object_name = "todo_to_delete"
    model = Todo
    template_name = "todo_delete.html"
    success_url = reverse_lazy("todolist")

class TodoUpdateView(UpdateView):
    context_object_name = "todo_to_update"
    model = Todo
    template_name = "todo_edit.html"
    success_url = reverse_lazy("todolist")
    form_class = TodoEditForm
