from django.db import models
from django.urls import reverse

class Todo(models.Model):
    task = models.CharField(max_length=200)
    author = models.ForeignKey(to="auth.User", on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    # TODO: maybe add some children tasks?

    def __str__(self):
        return self.task

    def get_absolute_url(self):
        return reverse("todo_detail", kwargs={"pk": self.pk})
    