def process_clients(deals):
    result = []

    for deal in deals:
        name = deal["name"]
        amount = deal["amount"]
        status = deal["status"]

        # 1. Перевірка типу суми
        # bool у Python є підкласом int, тому його теж відсікаємо
        if not isinstance(amount, (int, float)) or isinstance(amount, bool): 
            result.append({
                "name": name,
                "category": "фальшиві дані",
                "decision": "фальшиві дані"
            })
            continue

        # 2. Категорія за сумою
        if amount < 100:
            category = "Дрібнота"
        elif amount <= 999:
            category = "Середнячок"
        else:
            category = "Великий клієнт"

        # 3. Рішення за статусом
        match status:
            case "clean":
                decision = "працювати без питань"
            case "suspicious":
                decision = "перевірити документи"
            case "fraud":
                decision = "у чорний список"
            case _:
                decision = "невідомий статус"

        result.append({
            "name": name,
            "category": category,
            "decision": decision
        })

    return result


# Приклад даних
deals = [
    {"name": "Іван", "amount": 50, "status": "clean"},
    {"name": "Олена", "amount": 500, "status": "suspicious"},
    {"name": "Петро", "amount": 1500, "status": "fraud"},
    {"name": "Марія", "amount": 999, "status": "clean"},
    {"name": "Андрій", "amount": "1000", "status": "clean"},
    {"name": "Софія", "amount": 700, "status": "unknown"},
]

clients = process_clients(deals)

for client in clients:
    print(
        f"{client['name']}: "
        f"{client['category']} — "
        f"{client['decision']}"
    )
