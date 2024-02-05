import random

from django.core.management.base import BaseCommand, CommandParser
from django_seed import Seed
from manufacturer.management.commands.mfr_seed import run_seed as mfr_run_seed
from manufacturer.models import Manufacturer
from prod.models import (
    CateTypeChoices,
    Prod,
    ProdCategory,
    QualityAssuranceStatusChoices,
    SalesStatusChoices,
)

MODE_REFRESH = "refresh"
MODE_EMPTY = "empty"
seeder = Seed.seeder()


class Command(BaseCommand):
    help = "seed table prod for development and testing"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--mode", type=str, help="Mode")
        parser.add_argument("--nums", type=int, help="Numbers")
        return super().add_arguments(parser)

    def handle(self, *args, **options) -> str | None:
        self.stdout.write("seeding data...")
        run_seed(self, options["mode"], options["nums"])
        self.stdout.write("done")


def clear_data() -> None:
    Prod.objects.all().delete()


def init_categories(l_offset: int = 88, m_offset: int = 95, s_offset: int = 0) -> None:
    cate_type_list = []
    for i in range(0, 3):
        cate_id = f"{str(i + l_offset):0>6}"
        cate_name = "LL" + chr(ord("A") + i)
        cate_type_list.append((cate_id, cate_name, CateTypeChoices.Cate))
        for j in range(0, random.randint(2, 4)):
            child_cate_id = f"{cate_id[-4:]}{str(j + m_offset):0>2}"
            child_cate_name = cate_name + "MM" + chr(ord("A") + j)
            cate_type_list.append(
                (child_cate_id, child_cate_name, CateTypeChoices.SubCate)
            )
            for k in range(0, random.randint(2, 5)):
                sub_child_cate_id = f"{child_cate_id[-4:]}{str(k + s_offset):0>2}"
                sub_child_cate_name = child_cate_name + f"-{str(k + s_offset):0>6}"
                cate_type_list.append(
                    (sub_child_cate_id, sub_child_cate_name, CateTypeChoices.SubSubCate)
                )

    ProdCategory.objects.all().delete()
    for cate_id, cate_name, cate_type in cate_type_list:
        cate = {
            "cate_id": cate_id,
            "cate_name": cate_name,
            "cate_type": cate_type,
        }
        ProdCategory.objects.create(**cate)


def run_seed(self, mode: str, nums: int = 10) -> None:
    clear_data()
    if mode == MODE_EMPTY:
        return

    mfr_run_seed("refresh", nums=int(nums * 0.2))
    mfrs = Manufacturer.objects.all()

    categories = ProdCategory.objects.all()
    if categories.count() == 0:
        init_categories()
    categories = ProdCategory.objects.filter(cate_type=CateTypeChoices.SubSubCate)

    seeder.add_entity(
        Prod,
        nums,
        {
            "prod_name": lambda x: seeder.faker.name(),
            "prod_img": lambda x: "images/300_fzfQXUx.jpeg",
            "prod_quantity": lambda x: random.randint(1, 10),
            "prod_category": lambda x: random.choice(categories),
            "prod_effective_date": lambda x: seeder.faker.date(),
            "prod_sales_status": lambda x: random.choice(SalesStatusChoices.values),
            "prod_quality_assurance_status": lambda x: random.choice(
                QualityAssuranceStatusChoices.values
            ),
            "prod_mfr_id": lambda x: random.choice(mfrs),
        },
    )
    seeder.execute()
