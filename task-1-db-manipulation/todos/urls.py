from django.urls import path
from .views import TodoListView, TodoCreateView, TodoDeleteView, TodoUpdateView

urlpatterns = [
    path("", TodoListView.as_view(), name="todolist"),
    path("create/", TodoCreateView.as_view(), name="todocreate"),
    path("delete/<int:pk>/", TodoDeleteView.as_view(), name="tododelete"),
    path("edit/<int:pk>/", TodoUpdateView.as_view(), name="todoupdate")
]
