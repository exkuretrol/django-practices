from django import template

register = template.Library()


@register.filter
def index(indexable, i):
    """
    Returns the value at the given index.
    """
    return indexable[i]
