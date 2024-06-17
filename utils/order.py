import logging
from dataclasses import dataclass
from typing import List, Literal, Tuple, Union

from django.utils import timezone
from django.utils.translation import gettext as _
from rich.pretty import pretty_repr

from manufacturer.models import Manufacturer
from order.models import Order, OrderRule, OrderRuleTypeChoices
from prod.models import Prod, ProdCategory, UnitChoices

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class OrderProdSchema:
    prod_no: int
    prod_quantity: int


def validate_order(data: List[OrderProdSchema]):
    error_list = []
    prod_dict = dict()
    for order_product in data:
        try:
            prod = Prod.objects.get(prod_no=order_product.prod_no)
            prod_dict.update({prod: order_product.prod_quantity})
        except Prod.DoesNotExist:
            error_list.append(
                {
                    "code": "product_not_exist",
                    "message": f"Product {order_product.prod_no} not found",
                    "obj": order_product.prod_no,
                }
            )
            continue
    # check product rule
    for order_product in data:
        error_list += check_product_rule(order_product)

    # check product category rule
    error_list += check_category_rule(prod_dict)

    # check manufacturer rule
    error_list += check_manufacturer_rule(prod_dict)

    mfr_prod_dict = group_by(prod_dict, "manufacturer")
    return error_list, mfr_prod_dict


def check_product_rule(order_product: OrderProdSchema) -> List[dict]:
    error_list = []

    if isinstance(order_product.prod_no, int):
        prod = Prod.objects.get(prod_no=order_product.prod_no)
    else:
        prod = order_product.prod_no
    case_num = order_product.prod_quantity / (
        prod.prod_outer_quantity * prod.prod_inner_quantity
    )
    order_price = prod.prod_cost_price * order_product.prod_quantity
    prod_unit = UnitChoices(prod.prod_unit).label

    if order_product.prod_quantity <= 0:
        error_list.append(
            {
                "code": "quantity_too_low",
                "message": _("產品數量應大於 0 %(unit)s" % {"unit": prod_unit}),
                "obj": order_product.prod_no,
            }
        )
        return error_list

    rules = get_rule(prod, OrderRuleTypeChoices.Product)
    if rules.exists():
        obj_type = prod.__class__.__name__
        group_obj = prod
        if len(rules) > 1:
            logger.warning(
                "Multiple rules found for %(obj_type)s %(obj)s"
                % {"obj_type": obj_type, "obj": group_obj}
            )
            return error_list
        rule = rules.first()
        logger.debug(f"find a rule for product {prod}:\n{rule}")
        obj_type_name = OrderRuleTypeChoices(rule.or_type).label
        if rule.or_cannot_order:
            error_list.append(
                {
                    "code": "cannot_order",
                    "message": _(
                        "該%(obj_type_name)s目前無法下訂"
                        % {"obj_type_name": obj_type_name}
                    ),
                    "obj": order_product.prod_no,
                    "obj_type": obj_type,
                }
            )
            return error_list
        if rule.or_shipped_as_case:
            if not case_num.is_integer():
                error_list.append(
                    {
                        "code": "not_as_case",
                        "message": _(
                            "該%(obj_type_name)s的訂貨箱數應為整數，目前為：%(case_num).2f 箱"
                            % {
                                "obj_type_name": obj_type_name,
                                "case_num": case_num,
                            }
                        ),
                        "obj": order_product.prod_no,
                        "obj_type": obj_type,
                    }
                )
        if rule.or_order_price is not None:
            if order_price < rule.or_order_price:
                error_list.append(
                    {
                        "code": "order_product_price_too_low",
                        "message": _(
                            "該%(obj_type_name)s下訂總金額應大於 %(order_amount)i。"
                            % {
                                "obj_type_name": obj_type_name,
                                "order_amount": rule.or_order_price,
                            }
                        ),
                        "obj": order_product.prod_no,
                        "obj_type": obj_type,
                    }
                )
        if rule.or_order_cases_quantity is not None:
            if case_num < rule.or_order_cases_quantity:
                error_list.append(
                    {
                        "code": "order_quantity_too_low",
                        "message": _(
                            "該%(obj_type_name)s下訂數應大於 %(order_case_quantity)s 箱"
                            % {
                                "obj_type_name": obj_type_name,
                                "order_case_quantity": rule.or_order_cases_quantity,
                            }
                        ),
                        "obj": order_product.prod_no,
                        "obj_type": obj_type,
                    }
                )
    return error_list


def group_by(prod_dict: dict, key: Literal["category", "manufacturer"]):
    grouped_prods = dict()
    for prod, prod_quantity in prod_dict.items():
        if key == "manufacturer":
            group_obj = prod.prod_mfr_id
        else:
            group_obj = prod.prod_cate_no
        grouped_prods.setdefault(group_obj, []).append((prod, prod_quantity))
    logger.debug(f"classify by {key}:\n{pretty_repr(grouped_prods)}")
    return grouped_prods


def check_category_manufacturer_rule(
    group_obj: Union[Manufacturer, ProdCategory],
    group_prod_list: List[Tuple[Prod, int]],
    rule: OrderRule,
) -> List[dict]:
    error_list = []
    obj_type_name = OrderRuleTypeChoices(rule.or_type).label
    group_obj_name = group_obj.__class__.__name__
    if rule.or_cannot_order:
        error_list.append(
            {
                "code": "cannot_order",
                "message": _(
                    "該%(obj_type_name)s目前無法下訂" % {"obj_type_name": obj_type_name}
                ),
                "obj": str(group_obj),
                "obj_type": group_obj_name,
            }
        )
        return error_list

    if rule.or_order_price is not None:
        order_price = sum(
            prod.prod_cost_price * order_quantity
            for prod, order_quantity in group_prod_list
        )
        logger.debug(f"order_price: {order_price}")
        if order_price < rule.or_order_price:
            error_list.append(
                {
                    "code": "order_price_too_low",
                    "message": _(
                        "該%(obj_type_name)s下訂總金額應大於 %(order_amount)i。"
                        % {
                            "obj_type_name": obj_type_name,
                            "order_amount": rule.or_order_price,
                        }
                    ),
                    "obj": str(group_obj),
                    "obj_type": group_obj_name,
                }
            )
    return error_list


def check_category_rule(prod_dict: dict) -> List[dict]:
    error_list = []
    grouped_prod_dict = group_by(prod_dict, "category")
    for group_obj, group_prod_list in grouped_prod_dict.items():
        rules = get_rule(group_obj, OrderRuleTypeChoices.ProductCategory)
        group_obj_name = group_obj.__class__.__name__
        logger.debug(
            f"query rules for {group_obj_name}<{group_obj}>: {rules if len(rules) > 0 else None}"
        )
        if not rules.exists():
            # rule does not exist
            continue

        if len(rules) > 1:
            logger.warning(
                "找到多個%(obj_type)s %(obj)s的規則"
                % {"obj_type": group_obj_name, "obj": group_obj}
            )
            error_list.append(
                {
                    "code": "multiple_rules",
                    "message": _(
                        "找到多個%(obj_type)s %(obj)s的規則"
                        % {"obj_type": group_obj_name, "obj": group_obj}
                    ),
                    "obj": str(group_obj),
                    "obj_type": group_obj_name,
                }
            )
            continue

        rule = rules.first()
        error_list += check_category_manufacturer_rule(group_obj, group_prod_list, rule)

        # add more validation here

    return error_list


def check_manufacturer_rule(prod_dict: dict) -> List[dict]:
    error_list = []
    grouped_prod_dict = group_by(prod_dict, "manufacturer")
    for group_obj, group_prod_list in grouped_prod_dict.items():
        rules = get_rule(group_obj, OrderRuleTypeChoices.Manufacturer)
        group_obj_name = group_obj.__class__.__name__
        logger.debug(
            f"query rules for {group_obj_name}<{group_obj}>: {rules if len(rules) > 0 else None}"
        )
        if not rules.exists():
            # rule does not exist
            continue

        if len(rules) > 1:
            logger.warning(
                "找到多個%(obj_type)s %(obj)s的規則"
                % {"obj_type": group_obj_name, "obj": group_obj}
            )
            error_list.append(
                {
                    "code": "multiple_rules",
                    "message": _(
                        "找到多個%(obj_type)s %(obj)s的規則"
                        % {"obj_type": group_obj_name, "obj": group_obj}
                    ),
                    "obj": str(group_obj),
                    "obj_type": group_obj_name,
                }
            )
            continue

        rule = rules.first()
        error_list += check_category_manufacturer_rule(group_obj, group_prod_list, rule)

        # add more validation here

    return error_list


def get_order_no_from_day(day=timezone.localdate()):
    # TODO: order and timezone.now().date() didn't not sync,
    #       if user enter the order create page at 23:59:59,
    #       and then create an order at 00:00:00 (the form failed, and the user re-enter the form),
    #       the od_date will update, but the od_no didn't.
    day_str = day.strftime("%Y%m%d")

    # Month + 30
    # YYYYmmdd
    # 0123^
    day_str_list = list(day_str)
    day_str_list[4] = str(int(day_str[4]) + 3)
    day_str = "".join(day_str_list)

    orders = Order.objects.filter(od_no__startswith=day_str)

    if orders.exists():
        order_no = orders.last().od_no
    else:
        order_no = int(day_str + "00000")
    return order_no


def get_rule(
    or_item: Union[Prod, ProdCategory, Manufacturer], or_type: OrderRuleTypeChoices
):
    rules = OrderRule.objects.filter(
        or_type=or_type,
        or_effective_start_date__lte=timezone.now(),
        or_effective_end_date__gte=timezone.now(),
    )
    if or_type == OrderRuleTypeChoices.Product:
        rules = rules.filter(or_prod_no=or_item.pk)
    elif or_type == OrderRuleTypeChoices.ProductCategory:
        rules = rules.filter(or_prod_cate_no=or_item.pk)
    elif or_type == OrderRuleTypeChoices.Manufacturer:
        rules = rules.filter(or_mfr_id=or_item.pk)
    return rules
