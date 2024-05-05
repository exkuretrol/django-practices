from typing import List, Optional

from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from manufacturer.models import Manufacturer
from ninja import NinjaAPI, Schema
from ninja.responses import codes_4xx
from order.forms import get_order_no_from_day, get_rule
from order.models import Order, OrderProd, OrderRule, OrderRuleTypeChoices
from prod.models import (
    Prod,
    ProdCategory,
    QualityAssuranceStatusChoices,
    SalesStatusChoices,
)

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


class MessageSchema(Schema):
    message: str


class Error(MessageSchema):
    code: str
    obj: Optional[str | int] = None


class Errors(Schema):
    errors: List[Error]


class Success(MessageSchema):
    pass


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


@api.post("/order/orderproduct", response={200: Success, 400: Errors})
def create_order(request, data: OrderSchema):
    error_list = []
    order_mfr_id = None
    for order_product in data.products:
        try:
            product = Prod.objects.get(prod_no=order_product.prod_no)
            if order_mfr_id is None:
                order_mfr_id = product.prod_mfr_id
        except Prod.DoesNotExist:
            error_list.append(
                {
                    "code": "product_not_exist",
                    "message": f"Product {order_product.prod_no} not found",
                    "obj": order_product.prod_no,
                }
            )
            continue

        if order_product.prod_quantity <= 0:
            error_list.append(
                {
                    "code": "quantity_too_low",
                    "message": "Quantity should be greater than 0",
                    "obj": order_product.prod_no,
                }
            )
            continue

        p_rules = get_rule(product, OrderRuleTypeChoices.Product)
        if p_rules.exists():
            case_num = order_product.prod_quantity / (
                product.prod_outer_quantity * product.prod_inner_quantity
            )
            order_price = product.prod_cost_price * order_product.prod_quantity
            for p_rule in p_rules:
                if p_rule.or_cannot_order:
                    error_list.append(
                        {
                            "code": "cannot_order",
                            "message": "Product cannot be ordered",
                            "obj": order_product.prod_no,
                        }
                    )
                    continue
                if not p_rule.or_cannot_be_shipped_as_case:
                    if not case_num.is_integer():
                        error_list.append(
                            {
                                "code": "not_as_case",
                                "message": f"Case number should be integer for this product, current case number: {case_num:.2f}",
                                "obj": order_product.prod_no,
                            }
                        )
                if p_rule.or_order_amount is not None:
                    if order_price < p_rule.or_order_amount:
                        error_list.append(
                            {
                                "code": "order_amount_too_low",
                                "message": f"Order amount too low, minimum order amount: {p_rule.or_order_amount}",
                                "obj": order_product.prod_no,
                            }
                        )
                if p_rule.or_order_quantity_cases is not None:
                    print(p_rule.or_order_quantity_cases, case_num)
                    if case_num < p_rule.or_order_quantity_cases:
                        error_list.append(
                            {
                                "code": "order_quantity_too_low",
                                "message": f"Order quantity too low, minimum order case quantity: {p_rule.or_order_quantity_cases}",
                                "obj": order_product.prod_no,
                            }
                        )
    if len(error_list) != 0:
        return 400, {"errors": error_list}
    if data.action == "validation":
        return 200, {"message": "Order validated successfully"}
    order = Order.objects.create(
        od_no=get_order_no_from_day() + 1,
        od_mfr_id=order_mfr_id,
        od_except_arrival_date=timezone.localdate() + timezone.timedelta(days=7),
    )

    for order_product in data.products:
        product = Prod.objects.get(prod_no=order_product.prod_no)
        OrderProd.objects.create(
            op_od_no=order, op_prod_no=product, op_quantity=order_product.prod_quantity
        )

    return 200, {"message": f"Order {order.od_no} created successfully"}
