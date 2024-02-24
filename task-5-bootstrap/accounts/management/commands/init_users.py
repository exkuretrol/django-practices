from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandParser
from faker import Faker

User = get_user_model()


class Command(BaseCommand):
    help = "seed table prod for development and testing"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--nums", type=int, help="Numbers")
        return super().add_arguments(parser)

    def handle(self, *args, **options) -> str | None:
        self.stdout.write("seeding data...")
        init_users(options["nums"])
        self.stdout.write("done")


def empty_users():
    User.objects.exclude(username="kuaz").delete()


def init_users(nums: int = 10):
    empty_users()
    for _ in range(nums):
        u_name = Faker().user_name()
        u_pass = u_name + str("1234")
        User.objects.create_user(username=u_name, password=u_pass)
