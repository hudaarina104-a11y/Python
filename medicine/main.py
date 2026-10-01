from models import Medicine, Antibiotic, Vitamin, Vaccine


def print_medicines_info(medicines: list[Medicine]) -> None:
    for medicine in medicines:
        print(medicine.info())


medicines = [
    Antibiotic("Амоксицилін", 10, 45.50),
    Vitamin("Вітамін C", 20, 25.00),
    Vaccine("Пентаксим", 5, 350.00),
    Antibiotic("Азитроміцин", 8, 60.00),
    Vitamin("Вітамін D3", 15, 40.00),
]

print_medicines_info(medicines)