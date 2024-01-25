from typing import Any
from django.core.management.base import BaseCommand, CommandParser
from prod.models import Prod
from django_seed import Seed
import random

MODE_REFRESH = "refresh"
MODE_CLEAR = "clear"
seeder = Seed.seeder()


class Command(BaseCommand):
    help = "seed database prod for development and testing"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--mode", type=str, help="Mode")
        parser.add_argument("--nums", type=int, help="Numbers")
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("seeding data...")
        run_seed(self, options['mode'], options["nums"])
        self.stdout.write("done")

def clear_data() -> None:
    Prod.objects.all().delete()


def run_seed(self, mode: str, nums: int = 10) -> None:
    clear_data()
    if mode == MODE_CLEAR:
        return

    seeder.add_entity(
        Prod,
        nums,
        {
            "prod_name": lambda x: seeder.faker.name(),
            "prod_type": lambda x: random.choice(["T1", "T2", "T3"]),
            "prod_status": lambda x: random.choice(["AC", "IA"]),
            "prod_img": lambda x: random.choice(["images/300_fzfQXUx.jpeg"]),
            "prod_quantity": lambda x: random.randint(1, 10),
        },
    )
    seeder.execute()
