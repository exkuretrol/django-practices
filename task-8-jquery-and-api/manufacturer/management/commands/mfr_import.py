from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from accounts.management.commands.init_users import init_users
from accounts.models import CustomUser
from django.core.management.base import BaseCommand, CommandParser
from manufacturer.models import Manufacturer


class Command(BaseCommand):
    help = "import manufacturers from csv file"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--csv", type=str, help="path to csv file")
        parser.add_argument("--type", type=str, help="man/sub")
        return super().add_arguments(parser)

    def handle(self, *args, **options) -> str | None:
        self.stdout.write("importing data...")
        parse_csv(options["csv"], options["type"])

        self.stdout.write("done")


def empty():
    Manufacturer.objects.all().delete()


def parse_csv(filename: str, filetype: str):
    if filetype == "vendor":
        empty()
    users = CustomUser.objects.all()
    if users.count() == 0:
        init_users(1000)
        users = CustomUser.objects.all()
    curr_path = Path().cwd()
    path_to_file = curr_path / filename
    if filetype == "vendor":
        csv_header = [
            "VendorID",  # picked
            "VendorNM",  # picked
            "VendorSNM",
            "Manager",
            "ZipCode",
            "ZipCodeName1",
            "ZipCodeName2",
            "Address",
            "Tel",
            "Fax",
            "VendorCreDate",
            "EffDateFrom",
            "EffDateTo",
            "TranDateS",
            "TranDateE",
        ]
    else:
        csv_header = [
            "VendorID",  # picked
            "SubVendorID",  # picked
            "SubVendorNM",  # picked
            "OldVendorID",
            "VendorCAT",
            "Contacts",
            "OrderType",
            "LeadTime",
            "DeliverType",
            "SubVendorType",
            "SubVendorCreDate",
            "EffDateFrom",
            "EffDateTo",
            "TranDateS",
            "TranDateE",
            "AccountingType",
            "PaymentType",
            "BankID",
            "EftAccount",
            "PaymentArea",
            "CheckDay",
            "ReturnType",
            "InvoiceType",
            "ZipCode1",
            "ZipCodeName11",
            "ZipCodeName12",
            "SubVendorAdd1",
            "SubVendorTel1",
            "SubVendorFax1",
            "ZipCode2",
            "ZipCodeName21",
            "ZipCodeName22",
            "SubVendorAdd2",
            "SubVendorTel2",
            "SubVendorFax2",
            "ZipCode3",
            "ZipCodeName31",
            "ZipCodeName32",
            "SubVendorAdd3",
            "SubVendorTel3",
            "SubVendorFax3",
            "MinOrderAmount",
        ]

    if path_to_file.exists():
        df = pd.read_csv(path_to_file, header=0, dtype=str)
        df["VendorID"] = df["VendorID"].str.zfill(8)
        for _, row in df.iterrows():
            try:
                if filetype == "vendor":
                    address = row["ZipCodeName1"] + row["ZipCodeName2"]
                else:
                    address = row["ZipCodeName11"] + row["ZipCodeName12"]
                Manufacturer.objects.create(
                    mfr_main_id=row["VendorID"],
                    mfr_sub_id=(
                        "00"
                        if filetype == "vendor"
                        else row["SubVendorID"][-2:].zfill(2)
                    ),
                    mfr_name=(
                        row["VendorNM"] if filetype == "vendor" else row["SubVendorNM"]
                    ),
                    mfr_address=address,
                    mfr_user_id=np.random.choice(users),
                    mfr_created_at=(
                        row["VendorCreDate"]
                        if filetype == "vendor"
                        else row["SubVendorCreDate"]
                    ),
                )
            except Exception as e:
                print(e)
    else:
        exit()
