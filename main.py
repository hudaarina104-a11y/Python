# Розробник: Худа Ярина

def tokenize(expression):
    tokens = []
    i = 0
    n = len(expression)
    while i < n:
        char = expression[i]
        if char.isspace():
            i += 1
            continue
        if char in '+-*/()':
            tokens.append(char)
            i += 1
        elif char.isdigit() or char == '.':
            num_str = ''
            while i < n and (expression[i].isdigit() or expression[i] == '.'):
                num_str += expression[i]
                i += 1
            tokens.append(float(num_str))
        else:
            raise ValueError(f"Неприпустимий символ: {char}")
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def parse_expression(self):
        # Додавання та віднімання
        result = self.parse_term()
        while self.current() in ('+', '-'):
            op = self.current()
            self.pos += 1
            right = self.parse_term()
            if op == '+':
                result += right
            elif op == '-':
                result -= right
        return result

    def parse_term(self):
        # Множення та ділення
        result = self.parse_factor()
        while self.current() in ('*', '/'):
            op = self.current()
            self.pos += 1
            right = self.parse_factor()
            if op == '*':
                result *= right
            elif op == '/':
                if right == 0:
                    raise ZeroDivisionError("Ділення на нуль заборонено!")
                result /= right
        return result

    def parse_factor(self):
        # Числа, дужки та унарний мінус
        curr = self.current()
        if curr == '+':
            self.pos += 1
            return self.parse_factor()
        if curr == '-':
            self.pos += 1
            return -self.parse_factor()
        if curr == '(':
            self.pos += 1
            result = self.parse_expression()
            if self.current() != ')':
                raise ValueError("Пропущено закриваючу дужку ')'")
            self.pos += 1
            return result
        if isinstance(curr, (int, float)):
            self.pos += 1
            return curr
        raise ValueError("Синтаксична помилка у виразі")


def evaluate(expression_str):
    try:
        tokens = tokenize(expression_str)
        if not tokens:
            return "Порожній вхідний вираз"
        parser = Parser(tokens)
        result = parser.parse_expression()
        if parser.pos < len(tokens):
            raise ValueError("Некоректна структура виразу")
        return int(result) if result.is_integer() else result
    except Exception as e:
        return f"Помилка: {e}"


if __name__ == "__main__":
    expr = input("Введіть математичний вираз: ")
    print("Результат:", evaluate(expr))