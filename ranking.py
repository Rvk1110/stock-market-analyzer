import heapq
from typing import List, Tuple
from models import Stock
from storage import StockStorage

class RankingManager:
    def __init__(self, storage: StockStorage):
        self.storage = storage

    def calculate_priority_score(self, stock: Stock) -> float:
        return (stock.price * 0.5) + (stock.volume * 0.0001) - (stock.volatility * 50)

    def get_top_k_stocks(self, k: int, criteria: str = 'price') -> List[Stock]:
        all_stocks = self.storage.get_all_stocks()
        
        if criteria == 'price':
            return heapq.nlargest(k, all_stocks, key=lambda s: s.price)
        elif criteria == 'volume':
            return heapq.nlargest(k, all_stocks, key=lambda s: s.volume)
        elif criteria == 'score':
             return heapq.nlargest(k, all_stocks, key=lambda s: self.calculate_priority_score(s))
        else:
            return []

    def get_bottom_k_stocks(self, k: int, criteria: str = 'price') -> List[Stock]:
        all_stocks = self.storage.get_all_stocks()
        
        if criteria == 'price':
            return heapq.nsmallest(k, all_stocks, key=lambda s: s.price)
        elif criteria == 'volume':
            return heapq.nsmallest(k, all_stocks, key=lambda s: s.volume)
        else:
            return []

    def get_top_k_stocks_by_sector(self, sector: str, k: int, criteria: str = 'price') -> List[Stock]:
        sector_stocks = self.storage.get_stocks_by_sector(sector)
        if not sector_stocks:
            return []

        if criteria == 'price':
            return heapq.nlargest(k, sector_stocks, key=lambda s: s.price)
        elif criteria == 'volume':
            return heapq.nlargest(k, sector_stocks, key=lambda s: s.volume)
        elif criteria == 'score':
             return heapq.nlargest(k, sector_stocks, key=lambda s: self.calculate_priority_score(s))
        else:
            return []

