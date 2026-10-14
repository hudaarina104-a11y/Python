
from functools import wraps 


def get_amount(line):
    try:
        parts = line.split()

        if len(parts) != 2:
            return None

        amount = float(parts[1].replace(",", "."))

        return amount if amount >= 0 else None

    except ValueError:
        return None


def shadow(limit=200):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def generate():
                total = 0

                for line in func(*args, **kwargs):
                    print(line)

                    amount = get_amount(line)

                    if amount is not None:
                        total += amount

                        if total > limit:
                            print("Тіньовий ліміт перевищено. Активую схему.")

                    yield line

                return total

            return generate()

        return wrapper
    return decorator


def suspicious_counter(threshold=200):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def generate():
                total = 0
                warned = False

                for line in func(*args, **kwargs):
                    amount = get_amount(line)

                    if amount is not None:
                        total += amount

                        if total > threshold and not warned:
                            print("ПІДОЗРА! Сума перевищила поріг.")
                            warned = True

                    yield line

                return total

            return generate()

        return wrapper
    return decorator


@shadow(limit=200)
@suspicious_counter(threshold=300)
def transaction_generator():
    transactions = [
        "payment 120",
        "refund 50",
        "transfer 300",
        "payment abc",
        "payment 40",
    ]

    for transaction in transactions:
        yield transaction


if __name__ == "__main__":
    generator = transaction_generator()

    while True:
        try:
            next(generator)
        except StopIteration as result:
            print("Фінальна сума:", result.value)
            break
