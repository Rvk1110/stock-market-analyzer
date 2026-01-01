from dataclasses import dataclass, field
from typing import List

@dataclass
class Stock:
    """
    Represents a single stock entity.
    """
    symbol: str
    name: str
    sector: str
    price: float
    volume: int
    volatility: float  # A value between 0 and 1 representing volatility
    price_history: List[float] = field(default_factory=list)

    def update_price(self, new_price: float):
        """Updates price and appends to history."""
        self.price = new_price
        self.price_history.append(new_price)
        # Keep only last 50 prices for trend analysis to save memory if needed
        if len(self.price_history) > 100:
             self.price_history.pop(0)

    def __repr__(self):
        return f"Stock({self.symbol}, {self.name}, ${self.price}, {self.sector})"

if __name__ == "__main__":
    print("This is the data model module. Here is a demo of the Stock class:")
    demo_stock = Stock("TEST", "Test Company", "Technology", 100.0, 5000, 0.5)
    print(f"Created: {demo_stock}")
    demo_stock.update_price(105.0)
    print(f"Updated: {demo_stock} - History: {demo_stock.price_history}")

