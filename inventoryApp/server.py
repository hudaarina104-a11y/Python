
import csv
import math
import os
import tempfile

from datetime import datetime
from pathlib import Path
from threading import RLock

from flask import Flask, jsonify, request, send_file


app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
app.config["DATA_FILE"] = BASE_DIR / "data" / "inventory.csv"

FIELDS = [
    "id", "name", "category", "quantity",
    "price", "location", "created_at"
]

FILE_LOCK = RLock()


def csv_path():
    # Повертає шлях до CSV-файлу сервера
    return Path(app.config["DATA_FILE"])


def save_items(items):
    # Зберігає всі товари у CSV
    path = csv_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(
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

            for item in items:
                writer.writerow({
                    key: item.get(key, "")
                    for key in FIELDS
                })

        os.replace(temp_name, path)

    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def load_items():
    # Читає товари з CSV
    path = csv_path()

    if not path.exists():
        save_items([])

    with path.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        header = file.readline()
        file.seek(0)

        delimiter = (
            ";" if header.count(";") > header.count(",")
            else ","
        )

        reader = csv.DictReader(
            file, delimiter=delimiter
        )

        items = []

        for row in reader:
            items.append({
                "id": int(row["id"]),
                "name": row["name"],
                "category": row["category"],
                "quantity": int(row["quantity"]),
                "price": float(
                    row["price"].replace(",", ".")
                ),
                "location": row.get("location", ""),
                "created_at": row.get("created_at", "")
            })

        return items


def validated_fields(data):
    # Перевіряє дані, які надіслав клієнт
    if not isinstance(data, dict):
        raise ValueError(
            "Очікується JSON-об'єкт із полями товару."
        )

    name = data.get("name")
    category = data.get("category")
    location = data.get("location", "")
    quantity = data.get("quantity")
    price = data.get("price")

    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            "name має бути непорожнім рядком."
        )

    if not isinstance(category, str) or not category.strip():
        raise ValueError(
            "category має бути непорожнім рядком."
        )

    if not isinstance(location, str):
        raise ValueError(
            "location має бути рядком."
        )

    if type(quantity) is not int or quantity < 0:
        raise ValueError(
            "quantity має бути цілим невід'ємним числом."
        )

    if (
        type(price) not in (int, float)
        or not math.isfinite(price)
        or price < 0
    ):
        raise ValueError(
            "price має бути невід'ємним числом."
        )

    return {
        "name": name.strip(),
        "category": category.strip(),
        "quantity": quantity,
        "price": float(price),
        "location": location.strip()
    }


@app.get("/items")
def get_items():
    # GET /items — повертає всі товари
    with FILE_LOCK:
        return jsonify(load_items())


@app.post("/items")
def add_item():
    # POST /items — додає новий товар
    try:
        fields = validated_fields(
            request.get_json(silent=True)
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    with FILE_LOCK:
        items = load_items()

        new_id = max(
            (row["id"] for row in items),
            default=0
        ) + 1

        item = {
            "id": new_id,
            **fields,
            "created_at": datetime.now()
                .astimezone()
                .isoformat(timespec="seconds")
        }

        items.append(item)
        save_items(items)

        return jsonify(item), 201


@app.put("/items/<int:item_id>")
def edit_item(item_id):
    # PUT /items/id — редагує товар за ID
    try:
        fields = validated_fields(
            request.get_json(silent=True)
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    with FILE_LOCK:
        items = load_items()

        for row in items:
            if row["id"] == item_id:
                row.update(fields)
                save_items(items)
                return jsonify(row)

    return jsonify({
        "error": "Товар не знайдено."
    }), 404


@app.delete("/items/<int:item_id>")
def remove_item(item_id):
    # DELETE /items/id — видаляє товар
    with FILE_LOCK:
        items = load_items()

        remaining = [
            row for row in items
            if row["id"] != item_id
        ]

        if len(remaining) == len(items):
            return jsonify({
                "error": "Товар не знайдено."
            }), 404

        save_items(remaining)

        return jsonify({
            "message": "Товар видалено."
        })


@app.get("/export")
def export_csv():
    # GET /export — повертає серверний CSV
    with FILE_LOCK:
        load_items()

        return send_file(
            csv_path(),
            mimetype="text/csv",
            as_attachment=True,
            download_name="inventory.csv"
        )


if __name__ == "__main__":
    print(
        "Flask-сервер: http://127.0.0.1:5000",
        flush=True
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )
