# Розробник: Худа Ярина

def run_calculator():
    try:
        num1 = float(input("Введіть перше число: "))
        operator = input("Введіть операцію (+, -, *, /): ")
        num2 = float(input("Введіть друге число: "))

        if operator == '+':
            result = num1 + num2
        elif operator == '-':
            result = num1 - num2
        elif operator == '*':
            result = num1 * num2
        elif operator == '/':
            if num2 == 0:
                return "Помилка: ділення на нуль заборонено!"
            result = num1 / num2
        else:
            return "Помилка: невідомий оператор!"
        
        return f"Результат: {num1} {operator} {num2} = {result}"
        
    except ValueError:
        return "Помилка: потрібно вводити саме числа!"

print(run_calculator())