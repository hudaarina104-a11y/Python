from abc import ABC, abstractmethod


# Один предмет складу
class JunkItem:
    def __init__(self, name: str, quantity: int, value: float):
        self.name = name
        self.quantity = quantity
        self.value = value

    def __str__(self):
        return f"{self.name}: {self.quantity} шт., {self.value} грн"


# Інтерфейс сховища
class StorageBackend(ABC):

    @abstractmethod
    def save(self, items):
        pass

    @abstractmethod
    def load(self):
        pass


# Сховище у файлі
class JunkStorage(StorageBackend):

    def __init__(self, filename):
        self.filename = filename

    def save(self, items):
        with open(self.filename, "w", encoding="utf-8") as file:
            for item in items:
                value = str(item.value).replace(".", ",")
                file.write(f"{item.name}|{item.quantity}|{value}\n")

    def load(self):
        items = []

        with open(self.filename, "r", encoding="utf-8") as file:
            for number, line in enumerate(file, 1):
                parts = line.strip().split("|")

                if len(parts) != 3:
                    print(f"Попередження: рядок {number} пропущено")
                    continue

                try:
                    name = parts[0]
                    quantity = int(parts[1])
                    value = float(parts[2].replace(",", "."))
                except ValueError:
                    print(f"Попередження: рядок {number} пропущено")
                    continue

                items.append(JunkItem(name, quantity, value))

        return items


# Робота зі складом
class JunkRepository:

    def __init__(self, storage):
        self.storage = storage

    def add(self, item):
        items = self.storage.load()
        items.append(item)
        self.storage.save(items)

    def get_all(self):
        return self.storage.load()

    def find(self, name):
        return [
            item for item in self.storage.load()
            if item.name.lower() == name.lower()
        ]


# Демонстрація
if __name__ == "__main__":

    items = [
        JunkItem("Бляшанка", 5, 2.5),
        JunkItem("Стара плата", 3, 7.8),
        JunkItem("Купка дротів", 10, 1.2)
    ]

    storage = JunkStorage("junk.txt")
    repository = JunkRepository(storage)

    # Записуємо у файл
    storage.save(items)

    # Читаємо назад
    loaded_items = repository.get_all()

    print("Предмети зі складу:")

    for item in loaded_items:
        print(item)

    # Перевірка
    print("\nПеревірка:")

    for old, new in zip(items, loaded_items):
        if old.name == new.name and old.quantity == new.quantity and old.value == new.value:
            print(f"✓ {new.name} — все правильно")

    # Пошук
    print("\nПошук:")

    for item in repository.find("Стара плата"):
        print(item)