import pytest
# Замініть 'service_body_test' на точну назву вашого файлу з класом Order (без .py)
from order_manager import Order


# --- Тести для total() ---
def test_total_with_items():
    items = [
        {"price": 100, "quantity": 2},
        {"price": 50, "quantity": 1},
    ]
    order = Order(id=1, items=items)
    assert order.total() == 250


def test_total_empty_items():
    order = Order(id=2, items=[])
    assert order.total() == 0


# --- Тести для most_expensive() ---
def test_most_expensive_valid():
    items = [
        {"name": "A", "price": 10},
        {"name": "B", "price": 100},
        {"name": "C", "price": 50},
    ]
    order = Order(id=1, items=items)
    assert order.most_expensive() == {"name": "B", "price": 100}


def test_most_expensive_empty():
    order = Order(id=2, items=[])
    with pytest.raises(ValueError):
        order.most_expensive()


# --- Тести для apply_discount() ---
def test_apply_discount_valid():
    items = [
        {"price": 100, "quantity": 1},
        {"price": 200, "quantity": 2},
    ]
    order = Order(id=1, items=items)
    order.apply_discount(20)  # знижка 20%

    assert items[0]["price"] == 80.0
    assert items[1]["price"] == 160.0


def test_apply_discount_boundary_values():
    items = [{"price": 100, "quantity": 1}]
    
    # 0% знижки
    order1 = Order(id=1, items=[{"price": 100}])
    order1.apply_discount(0)
    assert order1.items[0]["price"] == 100.0

    # 100% знижки
    order2 = Order(id=2, items=[{"price": 100}])
    order2.apply_discount(100)
    assert order2.items[0]["price"] == 0.0


@pytest.mark.parametrize("invalid_percent", [-10, 105])
def test_apply_discount_invalid(invalid_percent):
    items = [{"price": 100, "quantity": 1}]
    order = Order(id=1, items=items)
    
    with pytest.raises(ValueError, match="Invalid discount"):
        order.apply_discount(invalid_percent)


# --- Тести для __repr__() ---
def test_repr():
    items = [{"price": 10}, {"price": 20}]
    order = Order(id=42, items=items)
    assert repr(order) == "<Order 42: 2 items>"