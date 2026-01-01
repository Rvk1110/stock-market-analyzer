from typing import List, Dict, Optional
from models import Stock

class StockStorage:
    def __init__(self):
        # Dynamic storage using Python List
        self.stocks_list: List[Stock] = []
        
        # O(1) Access using Dictionary (Hash Table)
        # Primary Key: Symbol
        self.stocks_map: Dict[str, Stock] = {}
        
        # Sector-wise classification
        self.sector_map: Dict[str, List[Stock]] = {}

    def add_stock(self, stock: Stock) -> bool:
        """
        Adds a new stock to storage.
        Time Complexity: O(1) Amortized
        """
        if stock.symbol in self.stocks_map:
            return False  # Duplicate symbol
        
        self.stocks_list.append(stock)
        self.stocks_map[stock.symbol] = stock
        
        if stock.sector not in self.sector_map:
            self.sector_map[stock.sector] = []
        self.sector_map[stock.sector].append(stock)
        
        return True

    def get_stock(self, symbol: str) -> Optional[Stock]:
        """
        Retrieves a stock by symbol.
        Time Complexity: O(1)
        """
        return self.stocks_map.get(symbol)

    def delete_stock(self, symbol: str) -> bool:
        """
        Deletes a stock from all data structures.
        Time Complexity: O(N) because of list removal. 
        Dictionary removal is O(1).
        """
        if symbol not in self.stocks_map:
            return False

        stock = self.stocks_map[symbol]
        
        # Remove from Map - O(1)
        del self.stocks_map[symbol]
        
        # Remove from List - O(N)
        self.stocks_list.remove(stock)
        
        # Remove from Sector Map - O(M) where M is stocks in that sector
        if stock.sector in self.sector_map:
            self.sector_map[stock.sector].remove(stock)
            
        return True

    def get_all_stocks(self) -> List[Stock]:
        return self.stocks_list

    def get_stocks_by_sector(self, sector: str) -> List[Stock]:
        return self.sector_map.get(sector, [])
