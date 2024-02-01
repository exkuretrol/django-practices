import random
from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django_seed import Seed
from manufacturer.models import Manufacturer
from pytz import timezone

MODE_REFRESH = "refresh"
MODE_EMPTY = "empty"
seeder = Seed.seeder()
tz = timezone("Asia/Taipei")


class Command(BaseCommand):
    help = "seed table manufacturer for development and testing"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--mode", type=str, help="Mode")
        parser.add_argument("--nums", type=int, help="Numbers")
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("seeding data...")
        run_seed(options["mode"], options["nums"])
        self.stdout.write("done")


def empty_data():
    Manufacturer.objects.all().delete()


def run_seed(mode: str, nums: int = 10):
    empty_data()

    if mode == MODE_EMPTY:
        return

    seeder.add_entity(
        Manufacturer,
        nums,
        {
            "mfr_name": lambda x: "Test Factory " + seeder.faker.name(),
            "mfr_location": lambda x: random.choice(
                ["Taipei", "Tainan", "Hsinchu", "Taichung", "Banqiao"]
            ),
            "mfr_created_at": lambda x: seeder.faker.date_time(tzinfo=tz),
            "mfr_updated_at": lambda x: seeder.faker.date_time(tzinfo=tz),
        },
    )
    seeder.execute()
