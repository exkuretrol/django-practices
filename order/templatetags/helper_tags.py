from django import forms, template

register = template.Library()


@register.filter
def index(indexable, i):
    """
    Returns the value at the given index.
    """
    return indexable[i]


@register.filter
def is_delete(field):
    return field.auto_id.endswith("DELETE")


@register.filter
def is_checked(field):
    return field.value()


@register.filter
def get_form_prefix(form):
    return form.prefix or "default"
