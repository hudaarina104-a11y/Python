
import threading
import random
import time


class Warehouse:
    def __init__(self, name, meds, price_per_unit):
        self.name = name
        self.meds = meds
        self.initial = meds
        self.price_per_unit = price_per_unit
        self.stolen = 0
        self.lock = threading.Lock()

    # Симуляція випадкової спроби крадіжки
    def steal(self, amount, use_lock=True):
        if use_lock:
            with self.lock:
                return self._steal(amount, False)
        return self._steal(amount, True)

    def _steal(self, amount, unsafe):
        # 20% шанс, що бігуна спіймають
        if random.random() < 0.2:
            return 0

        # Випадкова кількість медикаментів
        amount = random.randint(1, amount)

        available = self.meds

        # Без Lock створюємо умову гонки потоків
        if unsafe:
            time.sleep(0.001)

        stolen = min(amount, available)

        # Списуємо медикаменти
        self.meds = available - stolen
        self.stolen += stolen

        return stolen


class Runner(threading.Thread):
    def __init__(self, name, warehouse, use_lock=True,
                 show_progress=False):
        super().__init__()
        self.runner_name = name
        self.warehouse = warehouse
        self.use_lock = use_lock
        self.show_progress = show_progress
        self.profit = 0

    # Кожен потік виконує 10 спроб
    def run(self):
        for i in range(10):
            amount = random.randint(10, 30)

            stolen = self.warehouse.steal(
                amount, self.use_lock
            )

            self.profit += (
                stolen * self.warehouse.price_per_unit
            )

            # Смужка прогресу
            if self.show_progress:
                bar = "█" * (i + 1) + "░" * (9 - i)
                print(
                    f"{self.runner_name}: [{bar}] "
                    f"{(i + 1) * 10}%",
                    flush=True
                )

            time.sleep(random.uniform(0.1, 0.5))


# Перевіряємо три інваріанти
def check_invariants(warehouses, total_profit):
    for w in warehouses:
        assert w.meds >= 0, (
            f"{w.name}: від'ємна кількість!"
        )

        assert w.initial == w.meds + w.stolen, (
            f"{w.name}: порушено баланс медикаментів!"
        )

    expected_profit = sum(
        w.stolen * w.price_per_unit
        for w in warehouses
    )

    assert total_profit == expected_profit, (
        "Прибуток не відповідає кількості вкраденого!"
    )


# Один запуск симуляції
def simulation(use_lock=True, show_progress=False):
    warehouses = [
        Warehouse(
            f"Склад {i}",
            random.randint(100, 300),
            random.randint(10, 50)
        )
        for i in range(1, 4)
    ]

    runners = [
        Runner(
            f"Бігун {i}",
            random.choice(warehouses),
            use_lock,
            show_progress
        )
        for i in range(1, 6)
    ]

    # Запускаємо всі потоки
    for runner in runners:
        runner.start()

    # Чекаємо завершення всіх потоків
    for runner in runners:
        runner.join()

    total_profit = sum(r.profit for r in runners)

    if show_progress:
        print("\n--- ЗВІТ ---")
        for w in warehouses:
            print(
                f"{w.name}: було {w.initial}, "
                f"залишилось {w.meds}, "
                f"вкрадено {w.stolen}"
            )

        print(f"Загальний прибуток: {total_profit}")

    check_invariants(warehouses, total_profit)
    return total_profit


# Перевірка 100 запусків
def test_simulations(use_lock):
    for i in range(1, 101):
        try:
            simulation(use_lock)
        except AssertionError as error:
            print(f"Помилка на прогоні №{i}")
            print(f"Порушений інваріант: {error}")
            return

    print("Усі 100 прогонів пройшли успішно!")


if __name__ == "__main__":
    print("=== СИМУЛЯЦІЯ З LOCK ===")
    simulation(use_lock=True, show_progress=True)

    print("\n=== 100 ПРОГОНІВ З LOCK ===")
    test_simulations(use_lock=True)

    print("\n=== 100 ПРОГОНІВ БЕЗ LOCK ===")
    test_simulations(use_lock=False)
