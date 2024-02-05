import random
from typing import Any

import numpy as np
from accounts.management.commands.init_users import init_users
from accounts.models import CustomUser
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandParser
from django_seed import Seed
from faker import Faker
from manufacturer.models import Manufacturer
from pytz import timezone

seeder = Seed.seeder()
MODE_REFRESH = "refresh"
MODE_EMPTY = "empty"
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
    main = int(np.floor(nums * 0.3))
    sub = int(np.floor(nums * 0.7))
    init_users(nums=nums)
    users = CustomUser.objects.exclude(username="kuaz")
    empty_data()

    if mode == MODE_EMPTY:
        return

    seeder.add_entity(
        Manufacturer,
        main,
        {
            "mfr_id": lambda x: f"{np.random.random_integers(low=10**7, high=10**8-1):0>2}",
            "mfr_name": lambda x: "Test Factory " + seeder.faker.name(),
            "mfr_location": lambda x: np.random.choice(
                ["Taipei", "Tainan", "Hsinchu", "Taichung", "Banqiao"]
            ),
            "mfr_created_at": lambda x: seeder.faker.date_time(tzinfo=tz),
            "mfr_updated_at": lambda x: seeder.faker.date_time(tzinfo=tz),
            "mfr_user_id": lambda x: np.random.choice(users),
        },
    )
    seeder.execute()

    mfrs = Manufacturer.objects.all()
    seeder.add_entity(
        Manufacturer,
        sub,
        {
            "mfr_id": lambda x: random.choice(mfrs).mfr_id
            + f"{np.random.random_integers(low=1, high=99):0>2}",
            "mfr_name": lambda x: "Test Factory " + seeder.faker.name(),
            "mfr_location": lambda x: random.choice(
                ["Taipei", "Tainan", "Hsinchu", "Taichung", "Banqiao"]
            ),
            "mfr_created_at": lambda x: seeder.faker.date_time(tzinfo=tz),
            "mfr_updated_at": lambda x: seeder.faker.date_time(tzinfo=tz),
            "mfr_user_id": lambda x: random.choice(users),
        },
    )
    seeder.execute()
