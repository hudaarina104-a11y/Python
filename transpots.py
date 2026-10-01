from abc import ABC, abstractmethod


class Transport(ABC):
    def __init__(self, name: str, speed: int, capacity: int):
        self.name = name
        self.speed = speed
        self.capacity = capacity

    @abstractmethod
    def move(self, distance) -> float:
        "Повертає час у дорозі в годинах"
        pass

    @abstractmethod
    def fuel_consumption(self, distance) -> float:
        "Повертає витрати пального"
        pass

    @abstractmethod
    def info(self) -> str:
        "Повертає інформацію про транспорт"
        pass

    def calculate_cost(self, distance, price_per_unit) -> float:
        return self.fuel_consumption(distance) * price_per_unit


class Car(Transport):
    def move(self, distance) -> float:
        return distance / self.speed

    def fuel_consumption(self, distance) -> float:
        return distance * 0.07

    def info(self) -> str:
        return f"Автомобіль: {self.name}, швидкість: {self.speed} км/год"


class Bus(Transport):
    def __init__(self, name: str, speed: int, capacity: int, passengers: int):
        super().__init__(name, speed, capacity)
        self.passengers = passengers

    def move(self, distance) -> float:
        return distance / self.speed

    def fuel_consumption(self, distance) -> float:
        return distance * 0.15

    def info(self) -> str:
        if self.passengers > self.capacity:
            return f"Автобус: {self.name} — Перевантажено!"
        return (
            f"Автобус: {self.name}, швидкість: {self.speed} км/год, "
            f"пасажирів: {self.passengers}/{self.capacity}"
        )


class Bicycle(Transport):
    def move(self, distance) -> float:
        actual_speed = min(self.speed, 20)
        return distance / actual_speed

    def fuel_consumption(self, distance) -> float:
        return 0

    def info(self) -> str:
        actual_speed = min(self.speed, 20)
        return f"Велосипед: {self.name}, швидкість: {actual_speed} км/год"


class ElectricCar(Car):
    def battery_usage(self, distance) -> float:
        return distance * 0.2

    def fuel_consumption(self, distance) -> float:
        return 0


# Створюємо список різного транспорту
transports = [
    Car("Toyota", 100, 5),
    Bus("Mercedes", 80, 50, 45),
    Bus("City Bus", 60, 40, 45),
    Bicycle("Trek", 25, 1),
    ElectricCar("Tesla", 120, 5)
]


# Виводимо інформацію для кожного виду транспорту
distance = 100

for transport in transports:
    print(transport.info())
    print(f"Час на {distance} км: {transport.move(distance):.2f} год.")
    print(f"Витрати пального: {transport.fuel_consumption(distance):.2f}")

    if isinstance(transport, ElectricCar):
        print(f"Витрати батареї: {transport.battery_usage(distance):.2f}")

    print(f"Вартість: {transport.calculate_cost(distance, 60):.2f}")
    print("-" * 40)