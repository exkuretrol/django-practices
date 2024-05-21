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

    for _ in range(main):
        Manufacturer.objects.create(
            mfr_main_id=f"{np.random.random_integers(low=10**7, high=10**8-1):0>2}",
            mfr_sub_id="00",
            mfr_name="Test Factory " + seeder.faker.name(),
            mfr_address=np.random.choice(
                ["Taipei", "Tainan", "Hsinchu", "Taichung", "Banqiao"]
            ),
            mfr_user_id=np.random.choice(users),
        )

    mfrs = Manufacturer.objects.all()
    for _ in range(sub):
        try:
            Manufacturer.objects.create(
                mfr_main_id=np.random.choice(mfrs).mfr_main_id,
                mfr_sub_id=f"{np.random.random_integers(low=1, high=99):0>2}",
                mfr_name="Test Factory " + seeder.faker.name(),
                mfr_address=np.random.choice(
                    ["Taipei", "Tainan", "Hsinchu", "Taichung", "Banqiao"], 1
                )[0],
                mfr_user_id=np.random.choice(users),
            )
        except:
            pass
