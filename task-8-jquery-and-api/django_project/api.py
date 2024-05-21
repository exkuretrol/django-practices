import logging
from typing import List, Optional, Union

from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from manufacturer.models import Manufacturer
from ninja import NinjaAPI, Schema
from order.forms import get_order_no_from_day, get_rule
from order.models import Order, OrderProd, OrderRuleTypeChoices
from prod.models import (
    Prod,
    ProdCategory,
    QualityAssuranceStatusChoices,
    SalesStatusChoices,
    UnitChoices,
)
from rich.pretty import pretty_repr

logger = logging.getLogger(__name__)

api = NinjaAPI(urls_namespace="api")


class ProductCreate(Schema):
    prod_no: int
    prod_name: str
    prod_desc: Optional[str] = None
    prod_img: Optional[str] = None
    prod_quantity: int = 0
    prod_cate_no: str
    prod_sales_status: int = SalesStatusChoices.NORMAL
    prod_quality_assurance_status: int = QualityAssuranceStatusChoices.NORMAL
    prod_mfr_id: int


class ProductUpdate(Schema):
    prod_name: Optional[str] = None
    prod_desc: Optional[str] = None
    prod_img: Optional[str] = None
    prod_quantity: Optional[int] = None
    prod_cate_no: Optional[str] = None
    prod_sales_status: Optional[int] = None
    prod_quality_assurance_status: Optional[int] = None
    prod_mfr_id: Optional[int] = None


class ProductUpdateQuantity(Schema):
    prod_no: int
    prod_quantity: int


class ProductOutput(Schema):
    prod_no: int
    prod_name: str
    prod_desc: str | None
    prod_img: str
    prod_quantity: int
    prod_cate_no_id: str
    prod_sales_status: int
    prod_quality_assurance_status: int
    prod_mfr_id_id: int


class OrderProdSchema(Schema):
    prod_no: int
    prod_quantity: int


class OrderSchema(Schema):
    products: List[OrderProdSchema]
    action: str


class ChecklistSchema(Schema):
    mfr_full_id: str
    checklist: Optional[List[int]] = None
    unchecklist: Optional[List[int]] = None


class MessageSchema(Schema):
    message: str


class Error(MessageSchema):
    code: str
    obj: Optional[str | int] = None
    obj_type: Optional[str] = None


class Errors(Schema):
    errors: List[Error]


class Success(MessageSchema):
    obj: Optional[str | int] = None


@api.get("/product/{prod_no}", response={200: ProductOutput, 404: Error})
def get_product(request, prod_no: int):
    try:
        product = Prod.objects.get(prod_no=prod_no)
    except Prod.DoesNotExist:
        return 404, {"code": "product_not_exist", "message": "Product not found"}

    return 200, product.__dict__


@api.post(
    "/product",
    response={200: Success, 404: Error, 500: Error},
)
def create_product(request, data: ProductCreate | List[ProductCreate]):
    if not isinstance(data, list):
        try:
            product_category = ProdCategory.objects.get(cate_no=data.prod_cate_no)
        except ProdCategory.DoesNotExist:
            return 404, {"code": "category_not_exist", "message": "Category not found"}

        try:
            manufacturer = Manufacturer.objects.get(mfr_id=data.prod_mfr_id)
        except Manufacturer.DoesNotExist:
            return 404, {
                "code": "manufacturer_not_exist",
                "message": "Manufacturer not found",
            }
        try:
            product = Prod.objects.create(
                prod_no=data.prod_no,
                prod_name=data.prod_name,
                prod_desc=data.prod_desc,
                prod_img=data.prod_img,
                prod_quantity=data.prod_quantity,
                prod_cate_no=product_category,
                prod_sales_status=data.prod_sales_status,
                prod_quality_assurance_status=data.prod_quality_assurance_status,
                prod_mfr_id=manufacturer,
            )
        except IntegrityError:
            return 500, {
                "code": "product_already_exist",
                "message": "Product with this prod_no already exists",
            }
        return 200, {"message": "Product created successfully"}

    products = []
    for product_data in data:
        product_category = get_object_or_404(
            ProdCategory, cate_no=product_data.prod_cate_no
        )
        manufacturer = get_object_or_404(Manufacturer, mfr_id=product_data.prod_mfr_id)
        try:
            product = Prod.objects.get(prod_no=product_data.prod_no)
            if product:
                return 500, {
                    "code": "product_already_exist",
                    "message": "Product with this prod_no already exists",
                }
        except:
            pass
        product_data.prod_cate_no = product_category
        product_data.prod_mfr_id = manufacturer
        products.append(product_data)
    product_objects = []
    for product_data in products:
        product = Prod.objects.create(
            prod_no=product_data.prod_no,
            prod_name=product_data.prod_name,
            prod_desc=product_data.prod_desc,
            prod_img=product_data.prod_img,
            prod_quantity=product_data.prod_quantity,
            prod_cate_no=product_data.prod_cate_no,
            prod_sales_status=product_data.prod_sales_status,
            prod_quality_assurance_status=product_data.prod_quality_assurance_status,
            prod_mfr_id=product_data.prod_mfr_id,
        )
        product_objects.append(product)
    return 200, {"message": f"Products created successfully [{len(product_objects)}]"}


@api.put("/product/{prod_no}", response={200: ProductOutput, 404: Error})
def update_product(request, prod_no: int, data: ProductUpdate):
    try:
        product = Prod.objects.get(prod_no=prod_no)
    except product.DoesNotExist:
        return 404, {"code": "product_not_found", "message": "Product not found"}

    if "prod_mfr_id" in data and product.prod_mfr_id != data.prod_mfr_id:
        try:
            manufacturer = Manufacturer.objects.get(mfr_id=data.prod_mfr_id)
        except Manufacturer.DoesNotExist:
            return 404, {
                "code": "manufacturer_not_exist",
                "message": "Manufacturer not found",
            }
        data.prod_mfr_id = manufacturer

    if "prod_cate_no" in data and product.prod_cate_no != data.prod_cate_no:
        try:
            product_category = ProdCategory.objects.get(cate_no=data.prod_cate_no)
        except ProdCategory.DoesNotExist:
            return 404, {
                "code": "product_category_not_exist",
                "message": "Category not found",
            }
        data.prod_cate_no = product_category

    data = {k: v for k, v in data.dict().items() if v is not None}

    product.__dict__.update(**data)
    product.save()

    return 200, product


@api.put("/product", response={200: Success, 404: Error})
def update_products(request, data: List[ProductUpdateQuantity]):
    for product_data in data:
        try:
            product = Prod.objects.get(prod_no=product_data.prod_no)
        except product.DoesNotExist:
            return 404, {
                "code": "product_not_exist",
                "message": f"Product {product_data.prod_no} not found",
            }

        product.prod_quantity = product_data.prod_quantity
        product.save()

    return 200, {"message": "Products updated successfully"}


@api.post("/order", response={200: Success, 400: Errors})
def create_order(request, data: OrderSchema):
    error_list = []
    order_mfr_id = None
    prod_dict = dict()
    for order_product in data.products:
        try:
            prod = Prod.objects.get(prod_no=order_product.prod_no)
            if order_mfr_id is None:
                order_mfr_id = prod.prod_mfr_id
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

        # logger.debug(
        #     "current iteration:\n\t obj: %(obj_type)s\n\ttype: %(rule_type)s\n---\nrules: %(rules)s\n"
        #     % {
        #         "obj_type": obj.__str__(),
        #         "rule_type": rule_type.name,
        #         "rules": rules.__str__(),
        #     }
        # )
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

    for key in ["category", "manufacturer"]:
        grouped_prods = dict()
        for prod, l in prod_dict.items():
            if key == "manufacturer":
                group_obj = prod.prod_mfr_id
                rule_type = OrderRuleTypeChoices.Manufacturer
            else:
                group_obj = prod.prod_cate_no
                rule_type = OrderRuleTypeChoices.ProductCategory
            grouped_prods.setdefault(group_obj, []).append(prod)
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

    if len(error_list) != 0:
        logger.debug(f"error_list:\n{error_list}")
        return 400, {"errors": error_list}
    if data.action == "validation":
        return 200, {"message": _("訂單驗證成功")}
    elif data.action == "create":
        order = Order.objects.create(
            od_no=get_order_no_from_day() + 1,
            od_mfr_id=order_mfr_id,
            od_except_arrival_date=timezone.localdate() + timezone.timedelta(days=7),
        )

        for prod, order_quantity in prod_dict.items():
            OrderProd.objects.create(
                op_od_no=order, op_prod_no=prod, op_quantity=order_quantity
            )

        return 200, {
            "message": _("訂單 {od_no} 建立成功").format(od_no=order.od_no),
            "obj": order.od_no,
        }
    else:
        return 400, {"message": _("未知操作")}


@api.post("/checklist", response={200: Success, 400: Error})
def update_checklist(request, data: ChecklistSchema):
    logger.debug(data)
    if data.checklist:
        new_checklist = data.checklist

    if "checklist" in request.session:
        checklist_tuple_list = request.session.get("checklist")
        checklist_tuple = checklist_tuple_list[0]
        mfr_full_id, checklist = checklist_tuple
        logger.debug(f"(session)\nmfr_full_id: {mfr_full_id}, checklist: {checklist}")
        if mfr_full_id == data.mfr_full_id and len(checklist) > 0:
            checkset = set(checklist)
            if data.unchecklist:
                checkset = checkset.difference(set(data.unchecklist))
            if data.checklist:
                checkset = checkset.union(set(data.checklist))
            new_checklist = list(checkset)
            logger.debug("mfr_full_id matched")
            logger.debug(f"new checklist: {new_checklist}")
        else:
            logger.debug("mfr_full_id not matched")
    else:
        logger.debug("no checklist in session")

    new_checklist_tuple_list = [(data.mfr_full_id, new_checklist)]
    request.session["checklist"] = new_checklist_tuple_list
    logger.debug(f"new checklist tuple list: {new_checklist_tuple_list}")
    return {"message": _("成功更新"), "obj": str(new_checklist_tuple_list)}
