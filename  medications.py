def check_quantity(quantity):
    if isinstance(quantity, int) and not isinstance(quantity, bool):
        return True
    return False


def check_temperature(temperature):
    if isinstance(temperature, float):
        return True
    return False


def get_category(category):
    match category: 
        case "antibiotic":
            return "Рецептурний препарат"
        case "vitamin":
            return "Вільний продаж"
        case "vaccine":
            return "Потребує спецумов"
        case _:
            return "Невідома категорія"


def get_temperature_status(temperature):
    if temperature < 5:
        return "Холодно"
    elif temperature <= 25:
        return "Норма"
    else:
        return "Надто жарко"


def check_medication(medication):
    name = medication["name"]
    quantity = medication["quantity"]
    category = medication["category"]
    temperature = medication["temperature"]

    # Перевірка кількості та температури
    if not check_quantity(quantity) or not check_temperature(temperature):
        print(f"{name}: Помилка даних")
        return

    category_status = get_category(category)
    temperature_status = get_temperature_status(temperature)

    print(f"{name}: {category_status}, {temperature_status}")


# Список препаратів
medications = [
    {
        "name": "Амоксицилін",
        "quantity": 10,
        "category": "antibiotic",
        "temperature": 20.0
    },
    {
        "name": "Вітамін C",
        "quantity": 30,
        "category": "vitamin",
        "temperature": 27.0
    },
    {
        "name": "Вакцина",
        "quantity": 5,
        "category": "vaccine",
        "temperature": 2.0
    },
    {
        "name": "Препарат X",
        "quantity": 10,
        "category": "unknown",
        "temperature": 22.0
    },
    {
        "name": "Препарат Y",
        "quantity": "10",
        "category": "vitamin",
        "temperature": 20.0
    }
]


# Перевірка кожного препарату
for medication in medications:
    check_medication(medication)
