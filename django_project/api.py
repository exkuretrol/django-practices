import logging
from typing import List, Optional

from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from ninja import NinjaAPI, Schema

from manufacturer.models import Manufacturer
from order.models import Order, OrderProd
from prod.models import (
    Prod,
    ProdCategory,
    QualityAssuranceStatusChoices,
    SalesStatusChoices,
)
from utils.order import get_order_no_from_day

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
    prod_desc: Optional[str] = None
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


class ChecklistProductSchema(Schema):
    prod_no: int
    order_quantity: int


class ChecklistSchema(Schema):
    mfr_full_id: str
    checklist: Optional[List[ChecklistProductSchema]] = None
    unchecklist: Optional[List[ChecklistProductSchema]] = None


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
    from utils.order import validate_order

    error_list, mfr_prod_dict = validate_order(data.products)
    for mfr, prods in mfr_prod_dict.items():
        logger.debug(f"manufacturer: {mfr}")
        for prod, prod_quantity in prods:
            logger.debug(f"\tproduct: {prod}, quantity: {prod_quantity}")
    if len(error_list) != 0:
        logger.debug(f"error_list:\n{error_list}")
        return 400, {"errors": error_list}
    if data.action == "validation":
        return 200, {"message": _("訂單驗證成功")}
    elif data.action == "create":
        od_no_list = []
        for mfr, prods in mfr_prod_dict.items():
            # TODO: slice prods to multiple orders if prods exceed 5 or a specific number
            order = Order.objects.create(
                od_no=get_order_no_from_day() + 1,
                od_mfr_id=mfr,
                od_except_arrival_date=timezone.localdate()
                + timezone.timedelta(days=7),
            )

            od_no_list.append(str(order.od_no))

            for prod, order_quantity in prods:
                OrderProd.objects.create(
                    op_od_no=order, op_prod_no=prod, op_quantity=order_quantity
                )

        if "checklist" in request.session:
            request.session.pop("checklist")

        # TODO: implement for multiple orders
        od_no = od_no_list[0] if len(od_no_list) == 1 else ", ".join(od_no_list)
        return 200, {
            "message": _("訂單 {od_no} 建立成功").format(od_no=od_no),
            "obj": od_no,
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
        # promise that there is only one checklist tuple in the list
        [checklist_tuple] = checklist_tuple_list
        mfr_full_id, checklist = checklist_tuple
        logger.debug(f"(session)\nmfr_full_id: {mfr_full_id}, checklist: {checklist}")
        if mfr_full_id == data.mfr_full_id and len(checklist) > 0:
            new_checklist_dict = {c["prod_no"]: c["order_quantity"] for c in checklist}
            new_checklist_dict_keys = new_checklist_dict.keys()

            if data.unchecklist:
                unchecklist_prod_no_list = [c.prod_no for c in data.unchecklist]
                for prod_no in unchecklist_prod_no_list:
                    if prod_no in new_checklist_dict_keys:
                        new_checklist_dict.pop(prod_no)

            if data.checklist:
                for prod_order_quantity in data.checklist:
                    new_checklist_dict.update(
                        {
                            prod_order_quantity.prod_no: prod_order_quantity.order_quantity
                        }
                    )

            new_checklist_dict_list = [
                {"prod_no": k, "order_quantity": v}
                for k, v in new_checklist_dict.items()
            ]

            logger.debug("mfr_full_id matched")
            logger.debug(f"new checklist: {new_checklist_dict_list}")
        else:
            logger.debug("mfr_full_id not matched")
            new_checklist_dict_list = [c.dict() for c in new_checklist]
    else:
        logger.debug("no checklist in session")
        new_checklist_dict_list = [c.dict() for c in new_checklist]

    new_checklist_tuple_list = [(data.mfr_full_id, new_checklist_dict_list)]
    request.session["checklist"] = new_checklist_tuple_list
    logger.debug(f"new checklist tuple list: {new_checklist_tuple_list}")
    return {"message": _("成功更新"), "obj": str(new_checklist_tuple_list)}
