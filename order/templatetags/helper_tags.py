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


@register.filter
def is_order_category(url_name):
    return url_name in [
        "order_list",
        "order_create_clipboard",
        "order_create",
        "order_create_multiple",
        "order_update",
        "order_circulated_order",
    ]


@register.filter
def is_stock_category(url_name):
    return url_name in ["order_rules"]
