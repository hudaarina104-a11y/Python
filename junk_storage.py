from abc import ABC, abstractmethod


# 1. Клас одного предмета на складі
class JunkItem:
    def __init__(self, name: str, quantity: int, value: float):
        self.name = name
        self.quantity = quantity
        self.value = value

    def __str__(self):
        return f"{self.name}: кількість = {self.quantity}, ціна = {self.value}"


# 2. Інтерфейс для роботи зі сховищем
class StorageBackend(ABC):

    @abstractmethod
    def save(self, items: list[JunkItem]):
        pass

    @abstractmethod
    def load(self) -> list[JunkItem]:
        pass


# 3. Реалізація сховища через файл
class JunkStorage(StorageBackend):

    def __init__(self, filename: str):
        self.filename = filename

    # Зберігає список предметів у файл
    def save(self, items: list[JunkItem]):
        self.serialize(items, self.filename)

    # Завантажує предмети з файлу
    def load(self) -> list[JunkItem]:
        return self.parse(self.filename)

    # Запис у власному CSV-форматі
    def serialize(self, items: list[JunkItem], filename: str):
        with open(filename, "w", encoding="utf-8") as file:

            for item in items:
                # Крапку в десятковому числі замінюємо на кому
                value = str(item.value).replace(".", ",")

                # Поля розділяємо символом |
                file.write(
                    f"{item.name}|{item.quantity}|{value}\n"
                )

    # Читання з файлу
    def parse(self, filename: str) -> list[JunkItem]:
        items = []

        with open(filename, "r", encoding="utf-8") as file:

            for line_number, line in enumerate(file, start=1):

                # Прибираємо зайві пробіли та перенос рядка
                line = line.strip()

                # Порожній рядок пропускаємо
                if not line:
                    continue

                # Розділяємо рядок на поля
                parts = line.split("|")

                # Перевіряємо кількість полів
                if len(parts) != 3:
                    print(
                        f"Попередження: рядок {line_number} "
                        f"має неправильний формат. Пропущено."
                    )
                    continue

                name = parts[0]
                quantity_text = parts[1]
                value_text = parts[2]

                # Перевірка кількості
                try:
                    quantity = int(quantity_text)
                except ValueError:
                    print(
                        f"Попередження: рядок {line_number} "
                        f"має неправильну кількість. Пропущено."
                    )
                    continue

                # Перевірка ціни
                try:
                    # У файлі десятковий роздільник — кома
                    value = float(value_text.replace(",", "."))
                except ValueError:
                    print(
                        f"Попередження: рядок {line_number} "
                        f"має неправильну ціну. Пропущено."
                    )
                    continue

                # Створюємо об'єкт JunkItem
                item = JunkItem(name, quantity, value)

                items.append(item)

        return items


# 4. Клас, який працює зі складом
# Він НЕ знає, де саме зберігаються дані
class JunkRepository:

    def __init__(self, storage: StorageBackend):
        self.storage = storage

    # Додати предмет
    def add(self, item: JunkItem):
        items = self.storage.load()
        items.append(item)
        self.storage.save(items)

    # Отримати всі предмети
    def get_all(self) -> list[JunkItem]:
        return self.storage.load()

    # Знайти предмет за назвою
    def find(self, name: str) -> list[JunkItem]:
        items = self.storage.load()

        return [
            item for item in items
            if item.name.lower() == name.lower()
        ]


# 5. Демонстрація роботи програми
if __name__ == "__main__":

    # Створюємо предмети
    items = [
        JunkItem("Бляшанка", 5, 2.5),
        JunkItem("Стара плата", 3, 7.8),
        JunkItem("Купка дротів", 10, 1.2)
    ]

    # Створюємо сховище
    storage = JunkStorage("junk.txt")

    # Створюємо репозиторій
    repository = JunkRepository(storage)

    # Зберігаємо предмети
    storage.save(items)

    print("Предмети записано у файл.\n")

    # Читаємо предмети назад
    loaded_items = repository.get_all()

    print("Предмети після читання з файлу:")

    for item in loaded_items:
        print(item)

    # Перевірка правильності даних
    print("\nПеревірка:")

    for original, loaded in zip(items, loaded_items):

        if (
            original.name == loaded.name
            and original.quantity == loaded.quantity
            and original.value == loaded.value
        ):
            print(f"✓ {loaded.name} — дані збережені правильно")
        else:
            print(f"✗ {loaded.name} — помилка")

    # Пошук предмета
    print("\nПошук 'Стара плата':")

    found_items = repository.find("Стара плата")

    for item in found_items:
        print(item)