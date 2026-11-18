
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import api_client as api
from sync_service import InventoryService


class InventoryApp:
    def __init__(self, root):
        # Налаштовуємо головне вікно
        self.root = root
        self.root.title("Облік товарів")
        self.root.geometry("1100x680")
        self.root.minsize(900, 560)

        # Сервіс відповідає за сервер і локальний кеш
        self.service = InventoryService()
        self.products = self.service.products
        self.selected_id = None

        self._build_ui()
        self.refresh_table()

        # Перша синхронізація після запуску
        self.root.after(100, lambda: self.sync_now(silent=True))

        # Автоматична перевірка з'єднання кожні 10 секунд
        self.root.after(10000, self.auto_sync)

    def _build_ui(self):
        # Створюємо меню
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)

        file_menu.add_command(
            label="Синхронізувати зараз",
            command=self.sync_now
        )
        file_menu.add_command(
            label="Експорт CSV",
            command=self.export_csv
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Вихід",
            command=self.root.destroy
        )

        menu.add_cascade(label="Файл", menu=file_menu)
        self.root.config(menu=menu)

        # Пошук товарів
        search_frame = ttk.Frame(self.root, padding=(12, 10))
        search_frame.pack(fill="x")

        ttk.Label(
            search_frame,
            text="Пошук (назва / категорія):"
        ).pack(side="left")

        self.search_var = tk.StringVar()

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=35
        )
        search_entry.pack(side="left", padx=8)
        search_entry.bind(
            "<KeyRelease>",
            lambda _event: self.refresh_table()
        )

        ttk.Button(
            search_frame,
            text="Очистити пошук",
            command=self.clear_search
        ).pack(side="left")

        # Створюємо таблицю
        table_frame = ttk.Frame(self.root, padding=(12, 0))
        table_frame.pack(fill="both", expand=True)

        columns = (
            "id", "name", "category",
            "quantity", "price", "location"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "id": ("ID", 60),
            "name": ("Назва", 240),
            "category": ("Категорія", 160),
            "quantity": ("Кількість", 100),
            "price": ("Ціна", 110),
            "location": ("Склад / полиця", 180)
        }

        for col, (label, width) in headings.items():
            self.tree.heading(
                col,
                text=label,
                command=lambda c=col: self.sort_by(c)
            )

            self.tree.column(
                col,
                width=width,
                anchor="center"
                if col in ("id", "quantity", "price")
                else "w"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Форма для введення товару
        form = ttk.LabelFrame(
            self.root,
            text="Дані товару",
            padding=12
        )
        form.pack(fill="x", padx=12, pady=10)

        self.vars = {
            key: tk.StringVar()
            for key in (
                "name", "category", "quantity",
                "price", "location"
            )
        }

        labels = [
            ("name", "Назва"),
            ("category", "Категорія"),
            ("quantity", "Кількість"),
            ("price", "Ціна"),
            ("location", "Склад / полиця")
        ]

        for index, (key, label) in enumerate(labels):
            row, col = divmod(index, 3)

            ttk.Label(
                form,
                text=label
            ).grid(
                row=row * 2,
                column=col,
                sticky="w",
                padx=6
            )

            ttk.Entry(
                form,
                textvariable=self.vars[key],
                width=30
            ).grid(
                row=row * 2 + 1,
                column=col,
                sticky="ew",
                padx=6,
                pady=(2, 8)
            )

            form.columnconfigure(col, weight=1)

        # Кнопки керування товарами
        buttons = ttk.Frame(
            self.root,
            padding=(12, 0, 12, 10)
        )
        buttons.pack(fill="x")

        ttk.Button(
            buttons,
            text="Додати",
            command=self.add_product
        ).pack(side="left", padx=4)

        ttk.Button(
            buttons,
            text="Оновити вибраний",
            command=self.update_product
        ).pack(side="left", padx=4)

        ttk.Button(
            buttons,
            text="Видалити вибраний",
            command=self.delete_product
        ).pack(side="left", padx=4)

        ttk.Button(
            buttons,
            text="Очистити форму",
            command=self.clear_form
        ).pack(side="left", padx=4)

        # Статус-бар показує повідомлення і стан сервера
        self.status_var = tk.StringVar(value="Готово.")

        status = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w",
            padding=(8, 4)
        )
        status.pack(side="bottom", fill="x")

    def set_status(self, message):
        # Відображає повідомлення у нижній частині вікна
        self.status_var.set(message)

    def clear_search(self):
        self.search_var.set("")
        self.refresh_table()

    def validate_form(self):
        # Отримуємо дані з полів і перевіряємо їх
        name = self.vars["name"].get().strip()
        category = self.vars["category"].get().strip()
        quantity_text = self.vars["quantity"].get().strip()
        price_text = self.vars["price"].get().strip().replace(",", ".")
        location = self.vars["location"].get().strip()

        if not name or not category:
            raise ValueError(
                "Назва та категорія не можуть бути порожніми."
            )

        if not quantity_text:
            raise ValueError("Введіть кількість.")

        try:
            quantity = int(quantity_text)
        except ValueError:
            raise ValueError("Кількість має бути цілим числом.")

        if quantity < 0:
            raise ValueError("Кількість не може бути від'ємною.")

        if not price_text:
            raise ValueError("Введіть ціну.")

        try:
            price = float(price_text)
        except ValueError:
            raise ValueError("Ціна має бути числом.")

        if not math.isfinite(price) or price < 0:
            raise ValueError(
                "Ціна має бути невід'ємним скінченним числом."
            )

        return name, category, quantity, price, location

    def add_product(self):
        # CREATE — додаємо товар через сервер або локальний кеш
        try:
            message = self.service.add(*self.validate_form())

            self.products = self.service.products
            self.refresh_table()
            self.clear_form()
            self.set_status(message)

        except (ValueError, api.APIError, OSError) as error:
            self.show_error(error)

    def update_product(self):
        # UPDATE — змінюємо вибраний товар
        if self.selected_id is None:
            messagebox.showwarning(
                "Увага",
                "Спочатку виберіть товар у таблиці."
            )
            return

        try:
            message = self.service.update(
                self.selected_id,
                *self.validate_form()
            )

            self.products = self.service.products
            self.refresh_table()
            self.clear_form()
            self.set_status(message)

        except (ValueError, api.APIError, OSError) as error:
            self.show_error(error)

    def delete_product(self):
        # DELETE — видаляємо вибраний товар
        if self.selected_id is None:
            messagebox.showwarning(
                "Увага",
                "Спочатку виберіть товар у таблиці."
            )
            return

        product = self.find_product(self.selected_id)

        if messagebox.askyesno(
            "Підтвердження",
            f"Видалити товар «{product.name}»?"
        ):
            try:
                message = self.service.delete(self.selected_id)

                self.products = self.service.products
                self.clear_form()
                self.refresh_table()
                self.set_status(message)

            except (ValueError, api.APIError, OSError) as error:
                self.show_error(error)

    def clear_form(self):
        # Очищаємо всі поля форми
        for variable in self.vars.values():
            variable.set("")

        self.selected_id = None

        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def find_product(self, product_id):
        # Знаходимо товар за ID
        return next(
            p for p in self.products
            if p.id == product_id
        )

    def on_select(self, _event=None):
        # Показуємо дані вибраного товару у формі
        selected = self.tree.selection()

        if not selected:
            return

        product_id = int(selected[0])
        product = self.find_product(product_id)
        self.selected_id = product_id

        for key in self.vars:
            self.vars[key].set(str(getattr(product, key)))

        self.set_status(f"Вибрано товар ID {product_id}.")

    def refresh_table(self):
        # READ — оновлюємо таблицю й застосовуємо пошук
        query = self.search_var.get().strip().casefold()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for product in self.products:
            if (
                query
                and query not in product.name.casefold()
                and query not in product.category.casefold()
            ):
                continue

            self.tree.insert(
                "",
                "end",
                iid=str(product.id),
                values=(
                    product.id,
                    product.name,
                    product.category,
                    product.quantity,
                    f"{product.price:.2f}",
                    product.location
                )
            )

    def sort_by(self, column):
        # Сортуємо товари за вибраним стовпцем
        items = [
            (self.tree.set(item, column), item)
            for item in self.tree.get_children()
        ]

        reverse = getattr(
            self, "_sort_reverse", {}
        ).get(column, False)

        def key(pair):
            value = pair[0]
            try:
                return float(value)
            except ValueError:
                return value.casefold()

        items.sort(key=key, reverse=reverse)

        for index, (_, item) in enumerate(items):
            self.tree.move(item, "", index)

        if not hasattr(self, "_sort_reverse"):
            self._sort_reverse = {}

        self._sort_reverse[column] = not reverse

    def sync_now(self, silent=False):
        # Синхронізуємо кеш із Flask-сервером
        try:
            count = self.service.sync()

            self.products = self.service.products
            self.clear_form()
            self.refresh_table()

            self.set_status(
                f"Онлайн: синхронізовано {count} товарів."
            )

        except api.NetworkUnavailable:
            self.products = self.service.products
            self.refresh_table()
            self.set_status(
                "Офлайн: сервер недоступний, "
                "використовується cache.csv."
            )

        except (api.APIError, OSError, ValueError) as error:
            self.show_error(error, popup=not silent)

    def auto_sync(self):
        # Автоматична перевірка зв'язку кожні 10 секунд
        try:
            if not self.service.online or self.service.pending:
                self.sync_now(silent=True)
        finally:
            self.root.after(10000, self.auto_sync)

    def export_csv(self):
        # Експортуємо CSV, отриманий із сервера
        path = filedialog.asksaveasfilename(
            title="Експорт CSV",
            defaultextension=".csv",
            filetypes=[("CSV файли", "*.csv")]
        )

        if not path:
            return

        try:
            if self.service.pending:
                self.service.sync()

            content = api.export_csv()
            Path(path).write_bytes(content)

            self.set_status("CSV експортовано із сервера.")

        except api.NetworkUnavailable:
            self.set_status(
                "Експорт недоступний: сервер не працює."
            )

        except (api.APIError, OSError, ValueError) as error:
            self.show_error(error)

    def show_error(self, error, popup=True):
        # Повідомлення про помилки
        self.set_status(f"Помилка: {error}")

        if popup:
            messagebox.showerror("Помилка", str(error))


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
