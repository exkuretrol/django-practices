from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand, CommandParser
from prod.models import CateTypeChoices, ProdCategory


class Command(BaseCommand):
    help = "import product categiries from csv file"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--csv", type=str, help="Mode")
        return super().add_arguments(parser)

    def handle(self, *args, **options) -> str | None:
        self.stdout.write("importing data...")
        empty()
        parse_csv(options["csv"])
        self.stdout.write("done")


def empty():
    ProdCategory.objects.all().delete()


def parse_csv(filename: str):

    curr_path = Path().cwd()
    file_path = curr_path / filename
    if file_path.exists():
        c = Counter()
        c["Team"] = 0
        c["Invalid"] = 0
        with open(file=file_path, mode="r") as file:
            lines = [line.strip() for line in file]
            for i, line in enumerate(lines):
                if i == 0:
                    continue
                cate_id, cate_type, cate_name, parent_cate_id, _ = line.split(",")
                if cate_type == "T":
                    c["Team"] += 1
                    continue
                if (parent_cate_id != "00" + cate_id[:4]) & (cate_type != "1"):
                    print(
                        f"id: {cate_id}, name: {cate_name}, parent_id: {parent_cate_id}"
                    )
                    c["Invalid"] += 1
                    continue
                cate = ProdCategory.objects.create(
                    cate_id=cate_id, cate_name=cate_name, cate_type=int(cate_type)
                )
                cate.save()

        print(c)

    else:
        print(f"File {filename} not exist!")
        exit()
