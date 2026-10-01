from abc import ABC, abstractmethod


class Medicine(ABC):
    def __init__(self, name: str, quantity: int, price: float):
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        if not isinstance(quantity, int):
            raise TypeError("quantity must be an integer")

        if not isinstance(price, float):
            raise TypeError("price must be a float")

        self.name = name
        self.quantity = quantity
        self.price = price

    @abstractmethod
    def requires_prescription(self) -> bool:
        pass

    @abstractmethod
    def storage_requirements(self) -> str:
        pass

    def total_price(self) -> float:
        return self.quantity * self.price

    @abstractmethod
    def info(self) -> str:
        pass


class Antibiotic(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "8-15°C, темне місце"

    def info(self) -> str:
        return (
            f"Антибіотик: {self.name}, "
            f"кількість: {self.quantity}, "
            f"ціна: {self.price:.2f} грн, "
            f"загальна вартість: {self.total_price():.2f} грн, "
            f"рецепт: так, "
            f"зберігання: {self.storage_requirements()}"
        )


class Vitamin(Medicine):
    def requires_prescription(self) -> bool:
        return False

    def storage_requirements(self) -> str:
        return "15-25°C, сухо"

    def info(self) -> str:
        return (
            f"Вітамін: {self.name}, "
            f"кількість: {self.quantity}, "
            f"ціна: {self.price:.2f} грн, "
            f"загальна вартість: {self.total_price():.2f} грн, "
            f"рецепт: ні, "
            f"зберігання: {self.storage_requirements()}"
        )


class Vaccine(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "2-8°C, холодильник"

    def total_price(self) -> float:
        return super().total_price() * 1.10

    def info(self) -> str:
        return (
            f"Вакцина: {self.name}, "
            f"кількість: {self.quantity}, "
            f"ціна: {self.price:.2f} грн, "
            f"загальна вартість: {self.total_price():.2f} грн, "
            f"рецепт: так, "
            f"зберігання: {self.storage_requirements()}"
        )