
import json
from pathlib import Path
from csv_storage import CSVStorage
from product import Product
import api_client as api


class InventoryService:
    def __init__(self):
        folder = Path(__file__).parent
        self.cache_file = folder / "cache.csv"
        self.queue_file = folder / "pending_changes.json"
        self.storage = CSVStorage()
        self.products = self.storage.load(self.cache_file)
        self.pending = self.load_pending()
        self.online = False

    def load_pending(self):
        if self.queue_file.exists():
            with open(self.queue_file, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def save_cache(self):
        self.storage.save(self.cache_file, self.products)
        with open(self.queue_file, "w", encoding="utf-8") as file:
            json.dump(self.pending, file, ensure_ascii=False, indent=2)

    def sync(self):
        try:
            while self.pending:
                change = self.pending[0]
                operation = change["op"]
                item_id = change["id"]

                if operation == "post":
                    saved = api.add_item(change["data"])
                    self.products = [
                        Product.from_dict(saved) if p.id == item_id else p
                        for p in self.products
                    ]
                elif operation == "put":
                    api.update_item(item_id, change["data"])
                elif operation == "delete":
                    api.delete_item(item_id)

                self.pending.pop(0)
                self.save_cache()

            data = api.get_items()
            self.products = [Product.from_dict(row) for row in data]
            self.online = True
            self.save_cache()
            return len(self.products)

        except api.NetworkUnavailable:
            self.online = False
            raise

    def add(self, name, category, quantity, price, location):
        data = dict(name=name, category=category,
                    quantity=quantity, price=price, location=location)

        if not self.pending:
            try:
                saved = api.add_item(data)
                self.products.append(Product.from_dict(saved))
                self.online = True
                self.save_cache()
                return "Товар додано на сервер."
            except api.NetworkUnavailable:
                self.online = False

        temp_id = min([0] + [p.id for p in self.products]) - 1
        self.products.append(Product(temp_id, **data))
        self.pending.append({"op": "post", "id": temp_id, "data": data})
        self.save_cache()
        return "Офлайн: товар збережено в кеші."

    def update(self, item_id, name, category, quantity, price, location):
        data = dict(name=name, category=category,
                    quantity=quantity, price=price, location=location)

        product = next((p for p in self.products if p.id == item_id), None)
        if product is None:
            raise ValueError("Товар не знайдено.")

        if not self.pending:
            try:
                saved = api.update_item(item_id, data)
                self.products = [
                    Product.from_dict(saved) if p.id == item_id else p
                    for p in self.products
                ]
                self.online = True
                self.save_cache()
                return "Товар оновлено на сервері."
            except api.NetworkUnavailable:
                self.online = False

        for key, value in data.items():
            setattr(product, key, value)

        for change in self.pending:
            if change["id"] == item_id and change["op"] in ("post", "put"):
                change["data"] = data
                break
        else:
            self.pending.append({"op": "put", "id": item_id, "data": data})

        self.save_cache()
        return "Офлайн: зміни збережено."

    def delete(self, item_id):
        product = next((p for p in self.products if p.id == item_id), None)
        if product is None:
            raise ValueError("Товар не знайдено.")

        if not self.pending:
            try:
                api.delete_item(item_id)
                self.products = [p for p in self.products if p.id != item_id]
                self.online = True
                self.save_cache()
                return "Товар видалено із сервера."
            except api.NetworkUnavailable:
                self.online = False

        self.products = [p for p in self.products if p.id != item_id]

        if any(c["op"] == "post" and c["id"] == item_id for c in self.pending):
            self.pending = [c for c in self.pending if c["id"] != item_id]
        else:
            self.pending = [
                c for c in self.pending
                if not (c["id"] == item_id and c["op"] == "put")
            ]
            if not any(c["op"] == "delete" and c["id"] == item_id
                       for c in self.pending):
                self.pending.append({"op": "delete", "id": item_id})

        self.save_cache()
        return "Офлайн: видалення збережено."
