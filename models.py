from dataclasses import dataclass, field
from typing import List, Deque
from collections import deque

@dataclass
class Stock:
    symbol: str
    name: str
    sector: str
    price: float
    volume: int
    volatility: float
    price_history: deque = field(default_factory=lambda: deque(maxlen=100))

    def update_price(self, new_price: float):
        self.price = new_price
        self.price_history.append(new_price)

    def __repr__(self):
        return f"Stock({self.symbol}, {self.name}, ${self.price}, {self.sector})"

if __name__ == "__main__":
    print("This is the data model module. Here is a demo of the Stock class:")
    demo_stock = Stock("TEST", "Test Company", "Technology", 100.0, 5000, 0.5)
    print(f"Created: {demo_stock}")
    demo_stock.update_price(105.0)
    print(f"Updated: {demo_stock} - History: {demo_stock.price_history}")

