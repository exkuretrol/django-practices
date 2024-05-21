from django.db.models import Q


def prod_query(query: str) -> Q:
    conds = query.split(" ")
    filters = Q()
    for cond in conds:
        col, value = cond.split(":")
        if col == "name":
            filters &= Q(prod_name__contains=value)
        elif col == "desc":
            filters &= Q(prod_desc__contains=value)
        elif col == "type":
            filters &= Q(prod_type__contains=value)
        elif col == "status":
            filters &= Q(prod_status__contains=value)
    return filters
