from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand, CommandParser
from manufacturer.models import Manufacturer
from prod.models import Prod, ProdCategory


class Command(BaseCommand):
    help = "import products from csv file"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--csv", type=str, help="Mode")
        return super().add_arguments(parser)

    def handle(self, *args, **options) -> str | None:
        self.stdout.write("importing data...")
        empty()
        parse_csv(options["csv"])
        self.stdout.write("done")


def empty():
    Prod.objects.all().delete()


def parse_csv(filename: str):

    curr_path = Path().cwd()
    path_to_file = curr_path / filename
    c = Counter()
    csv_header = [
        "ItemCode",
        "ItemNM",
        "ItemShelfNM",
        "ItemInvNM",
        "NewItemDate",
        "StSaleDate",
        "EnSaleDate",
        "EffDateFrom",
        "EffDateTo",
        "CatID1",
        "CatID2",
        "CatID3",
        "TaxType",
        "ItemType",
        "ChargeType",
        "NoChargeReason",
    ]

    mfrs = Manufacturer.objects.all()
    if path_to_file.exists():
        empty()
        df = pd.read_csv(path_to_file, skiprows=1, names=csv_header, dtype=str)
        df["CatID1"] = df["CatID1"].str.zfill(2)
        df["CatID2"] = df["CatID2"].str.zfill(4)
        df["CatID3"] = df["CatID3"].str.zfill(6)
        for _, row in df.iterrows():
            if (
                (row["CatID1"] != row["CatID2"][:2])
                or (row["CatID1"] != row["CatID3"][:2])
                or (row["CatID2"][2:4] != row["CatID3"][2:4])
            ):
                c["Invalid"] += 1
                print(row)
                continue

            try:
                cate = ProdCategory.objects.get(cate_no=row["CatID3"])
            except ProdCategory.DoesNotExist as e:
                cate = None

            if cate is None:
                c["Category does Not Exist"] += 1
                continue

            try:
                Prod.objects.create(
                    prod_no=int(row["ItemCode"]),
                    prod_name=row["ItemNM"],
                    prod_cate_no=cate,
                    prod_mfr_id=np.random.choice(mfrs),
                )
            except:
                c["Duplicated"] += 1

        print(c)

    else:
        print(f"File {filename} not exist!")
        exit()
