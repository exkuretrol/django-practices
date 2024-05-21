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
        # parse_csv(options["csv"])
        parse_csv_v2(options["csv"])

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


def parse_csv_v2(filename: str):
    curr_path = Path().cwd()
    path_to_file = curr_path / filename
    if path_to_file.exists():
        df = pd.read_csv(path_to_file, header=0, dtype=str)
        df = df.astype(
            {
                "product_no": int,
                "sale_status": int,
                "product_unit": int,
                "outer_quantity": float,
                "inner_quantity": float,
                "sell_zone": str,
                "qa_status": int,
                "manufacturer_id": str,
                "effective_start_date": str,
                "effective_end_date": str,
                "cost_price": float,
                "retail_price": float,
                "product_name": str,
                "category": str,
                "sub_category": str,
                "sub_sub_category": str,
            }
        )
        df["category"] = df["category"].str.replace(".0", "").str.zfill(6)
        df["sub_category"] = df["sub_category"].str.replace(".0", "").str.zfill(6)
        df["sub_sub_category"] = (
            df["sub_sub_category"].str.replace(".0", "").str.zfill(6)
        )
        df["outer_quantity"] = df["outer_quantity"].astype(int)
        df["inner_quantity"] = df["inner_quantity"].astype(int)
        for _, row in df.iterrows():
            try:
                mfr_id = row["manufacturer_id"].zfill(10)
                mfr = Manufacturer.objects.get(mfr_full_id=mfr_id)
                cate_no = ProdCategory.objects.get(cate_no=row["sub_sub_category"])
                Prod.objects.create(
                    prod_no=row["product_no"],
                    prod_name=row["product_name"],
                    prod_unit=row["product_unit"],
                    prod_effective_start_date=row["effective_start_date"],
                    prod_effective_end_date=row["effective_end_date"],
                    prod_sales_status=row["sale_status"],
                    prod_quality_assurance_status=row["qa_status"],
                    prod_cate_no=cate_no,
                    prod_cost_price=row["cost_price"],
                    prod_retail_price=row["retail_price"],
                    prod_sell_zone=row["sell_zone"],
                    prod_outer_quantity=row["outer_quantity"],
                    prod_inner_quantity=row["inner_quantity"],
                    prod_mfr_id=mfr,
                )
            except Exception as e:
                print(f"{row["sub_sub_category"]}")

    else:
        print(f"File {filename} not exist!")
        exit()
