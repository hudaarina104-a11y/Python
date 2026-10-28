
def parse(line):
    try:
        op, value = line.split()
        value = float(value)
        if op not in ("payment", "refund", "transfer"):
            return None
        return -value if op == "refund" else value
    except (ValueError, TypeError):
        return None


def shadow(limit=200):
    def decorator(func):
        def wrapper(*args, **kwargs):
            total = 0
            for line in func(*args, **kwargs):
                print(line)
                amount = parse(line)
                if amount is not None:
                    total += amount
                    if total > limit:
                        print("Тіньовий ліміт перевищено. Активую схему")
                        limit_check = True
                        break
                yield line
            return total
        return wrapper
    return decorator


def suspicious_counter(threshold=400):
    def decorator(func):
        def wrapper(*args, **kwargs):
            total = 0
            warned = False
            for line in func(*args, **kwargs):
                amount = parse(line)
                if amount is not None:
                    total += amount
                    if total > threshold and not warned:
                        print("Підозріла сума!")
                        warned = True
                yield line
            return total
        return wrapper
    return decorator


@suspicious_counter(threshold=400)
@shadow(limit=200)
def transactions():
    yield from [
        "payment 120",
        "refund 50",
        "transfer 300",
        "payment 80",
        "payment abc",
        "unknown 500",
    ]


g = transactions()
while True:
    try:
        next(g)
    except StopIteration as e:
        print("Фінальна сума:", e.value)
        break
