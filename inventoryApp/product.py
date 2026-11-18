from dataclasses import dataclass
from datetime import datetime


@dataclass
class Product:
    id: int
    name: str
    category: str
    quantity: int
    price: float
    location: str
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price,
            "location": self.location,
            "created_at": self.created_at,
        }

    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
            category=str(data["category"]),
            quantity=int(data["quantity"]),
            price=float(data["price"]),
            location=str(data.get("location", "")),
            created_at=str(data.get("created_at", ""))
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price,
            "location": self.location,
            "created_at": self.created_at
        }
