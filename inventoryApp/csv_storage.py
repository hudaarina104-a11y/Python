
import csv
import os
import tempfile
from pathlib import Path
from product import Product

FIELDS = [
    "id", "name", "category", "quantity",
    "price", "location", "created_at"
]


class CSVStorage:
    def load(self, filename):
        # Завантажуємо товари із CSV
        path = Path(filename)

        if not path.exists():
            return []

        with path.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            sample = file.read(2048)
            file.seek(0)

            try:
                dialect = (
                    csv.Sniffer().sniff(sample, delimiters=",;")
                    if sample.strip()
                    else csv.excel
                )
            except csv.Error:
                dialect = csv.excel

            reader = csv.DictReader(file, dialect=dialect)

            if not reader.fieldnames:
                return []

            required = {
                "id", "name", "category", "quantity", "price"
            }

            if not required.issubset(set(reader.fieldnames)):
                raise ValueError(
                    "CSV має містити id, name, "
                    "category, quantity, price"
                )

            return [
                Product.from_dict(row)
                for row in reader
            ]

    def save(self, filename, products):
        # Зберігаємо список товарів у CSV
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        fd, tmp = tempfile.mkstemp(
            dir=path.parent,
            prefix=".inventory_",
            suffix=".tmp"
        )

        try:
            with os.fdopen(
                fd, "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.DictWriter(
                    file, fieldnames=FIELDS
                )
                writer.writeheader()

                for product in products:
                    writer.writerow(product.to_dict())

            os.replace(tmp, path)

        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
