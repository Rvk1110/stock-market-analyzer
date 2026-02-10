from typing import List, Dict, Optional
from models import Stock

class StockStorage:
    def __init__(self):
        self.stocks_list: List[Stock] = []
        self.stocks_map: Dict[str, Stock] = {}
        self.sector_map: Dict[str, List[Stock]] = {}

    def add_stock(self, stock: Stock) -> bool:
        if stock.symbol in self.stocks_map:
            return False
        
        self.stocks_list.append(stock)
        self.stocks_map[stock.symbol] = stock
        
        if stock.sector not in self.sector_map:
            self.sector_map[stock.sector] = []
        self.sector_map[stock.sector].append(stock)
        
        return True

    def get_stock(self, symbol: str) -> Optional[Stock]:
        return self.stocks_map.get(symbol)

    def delete_stock(self, symbol: str) -> bool:
        if symbol not in self.stocks_map:
            return False

        stock = self.stocks_map[symbol]
        
        del self.stocks_map[symbol]
        self.stocks_list.remove(stock)
        
        if stock.sector in self.sector_map:
            self.sector_map[stock.sector].remove(stock)
            
        return True

    def get_all_stocks(self) -> List[Stock]:
        return self.stocks_list

    def get_stocks_by_sector(self, sector: str) -> List[Stock]:
        return self.sector_map.get(sector, [])
