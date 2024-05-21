from datetime import timedelta
from typing import Any

import numpy as np
from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone
from faker import Faker
from manufacturer.models import Manufacturer
from order.forms import get_order_no_from_day
from order.models import (
    Order,
    OrderProd,
    StatusChoices,
    WarehouseStorageFeeRecipientChoices,
)

faker = Faker()
MODE_REFRESH = "refresh"
MODE_EMPTY = "empty"
end_date = timezone.datetime.now(tz=timezone.get_current_timezone())
start_date = end_date - timezone.timedelta(weeks=4)


class Command(BaseCommand):
    help = "seed table order for development and testing"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--mode", type=str, help="Mode")
        parser.add_argument("--nums", type=int, help="Numbers")
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("seeding data...")
        run_seed(options["mode"], options["nums"])
        self.stdout.write("done")


def empty_data():
    Order.objects.all().delete()


def run_seed(mode: str, nums: int = 10):
    empty_data()

    if mode == MODE_EMPTY:
        return

    for _ in range(nums):
        # random choose between days
        random_date = start_date + timezone.timedelta(
            days=np.random.randint(0, (end_date - start_date).days)
        )

        od_no = get_order_no_from_day(random_date) + 1
        od_has_contact_form = np.random.choice([True, False], p=[0.2, 0.8])

        od = Order.objects.create(
            od_no=od_no,
            od_mfr_id=np.random.choice(Manufacturer.objects.all()),
            od_date=random_date,
            od_except_arrival_date=random_date
            + timedelta(days=np.random.randint(3, 10)),
            od_has_contact_form=od_has_contact_form,
            od_contact_form_no=(
                np.random.random_integers(0, nums) if od_has_contact_form else None
            ),
            od_warehouse_storage_fee_recipient=np.random.choice(
                WarehouseStorageFeeRecipientChoices, p=[0.8, 0.1, 0.1]
            ),
            od_notes=np.random.choice(["", faker.text()], p=[0.8, 0.2]),
            od_contact_form_notes=np.random.choice(["", faker.text()], p=[0.8, 0.2]),
        )
        od.save()

        prods = od.od_mfr_id.prod_set.all()
        max_prods = len(prods)
        if max_prods == 0:
            od.delete()
            continue
        if max_prods > 5:
            max_prods = 5
        selected_prods = np.random.choice(
            prods,
            replace=False,
            size=np.random.choice(range(1, max_prods + 1), 1),
        )
        for prod in selected_prods:
            op = OrderProd.objects.create(
                op_od_no=od,
                op_prod_no=prod,
                op_quantity=np.random.randint(1, 10),
                op_status=np.random.choice(StatusChoices),
            )
            op.save()
