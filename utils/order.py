import logging
from dataclasses import dataclass
from typing import List

from django.utils.translation import gettext as _
from rich.pretty import pretty_repr

from django_project.api import OrderProdSchema
from order.forms import get_rule
from order.models import OrderRuleTypeChoices
from prod.models import Prod, UnitChoices

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
            continue

        rules = get_rule(prod, OrderRuleTypeChoices.Product)
        if rules.exists():
            obj_type = prod.__class__.__name__
            group_obj = prod
            if len(rules) > 1:
                logger.warning(
                    "Multiple rules found for %(obj_type)s %(obj)s"
                    % {"obj_type": obj_type, "obj": group_obj}
                )
                break
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
                continue
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
    logger.debug(f"product dict:\n{pretty_repr(prod_dict)}")

    mfr_prod_dict = dict()
    for key in ["category", "manufacturer"]:
        grouped_prods = dict()
        for prod, prod_quantity in prod_dict.items():
            if key == "manufacturer":
                group_obj = prod.prod_mfr_id
                rule_type = OrderRuleTypeChoices.Manufacturer
            else:
                group_obj = prod.prod_cate_no
                rule_type = OrderRuleTypeChoices.ProductCategory
            grouped_prods.setdefault(group_obj, []).append(prod)
            if key == "manufacturer":
                mfr_prod_dict.setdefault(group_obj, []).append((prod, prod_quantity))
        logger.debug(f"classify by {key}:\n{pretty_repr(grouped_prods)}")

        for group_obj, group_prod_list in grouped_prods.items():
            rules = get_rule(group_obj, rule_type)
            obj_type = group_obj.__class__.__name__
            logger.debug(
                f"query rules for {obj_type}<{group_obj}>: {rules if len(rules) > 0 else None}"
            )

            if len(rules) > 1:
                logger.warning(
                    "Multiple rules found for %(obj_type)s %(obj)s"
                    % {"obj_type": obj_type, "obj": group_obj}
                )
                error_list.append(
                    {
                        "code": "multiple_rules",
                        "message": _(
                            "找到多個%(obj_type)s %(obj)s的規則"
                            % {"obj_type": obj_type, "obj": group_obj}
                        ),
                        "obj": str(group_obj),
                        "obj_type": obj_type,
                    }
                )
                continue
            if not rules.exists():
                # rule does not exist
                continue
            rule = rules.first()
            obj_type_name = OrderRuleTypeChoices(rule.or_type).label

            if rule.or_cannot_order:
                error_list.append(
                    {
                        "code": "cannot_order",
                        "message": _(
                            "該%(obj_type_name)s目前無法下訂"
                            % {"obj_type_name": obj_type_name}
                        ),
                        "obj": str(group_obj),
                        "obj_type": obj_type,
                    }
                )
                continue
            if rule.or_order_price is not None:
                order_price = sum(
                    prod.prod_cost_price * order_quantity
                    for prod, order_quantity in prod_dict.items()
                    if prod in group_prod_list
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
                            "obj_type": obj_type,
                        }
                    )
    return error_list, mfr_prod_dict
