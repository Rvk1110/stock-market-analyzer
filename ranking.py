import heapq
from typing import List, Tuple
from models import Stock
from storage import StockStorage

class RankingManager:
    def __init__(self, storage: StockStorage):
        self.storage = storage

    def calculate_priority_score(self, stock: Stock) -> float:
        """
        Calculates a priority score based on:
        - Price Change (approximated here by price/100 for simplicity as we lack prev close in basic model, 
          but in full impl we would calculate actual gain %)
        - Volume (weighted)
        - Volatility
        
        Formula: (Price * 0.4) + (Volume * 0.001) - (Volatility * 100)
        (This is arbitrary for demonstration)
        """
        # Improved simplistic scoring for demo
        # Higher price, higher volume, lower volatility = higher score
        return (stock.price * 0.5) + (stock.volume * 0.0001) - (stock.volatility * 50)

    def get_top_k_stocks(self, k: int, criteria: str = 'price') -> List[Stock]:
        """
        Get Top K stocks based on criteria efficiently using Heaps.
        Time Complexity: O(N log K) using nlargest.
        """
        all_stocks = self.storage.get_all_stocks()
        
        if criteria == 'price':
            # Max Heap approach using nlargest
            return heapq.nlargest(k, all_stocks, key=lambda s: s.price)
        elif criteria == 'volume':
            return heapq.nlargest(k, all_stocks, key=lambda s: s.volume)
        elif criteria == 'score':
             return heapq.nlargest(k, all_stocks, key=lambda s: self.calculate_priority_score(s))
        else:
            return []

    def get_bottom_k_stocks(self, k: int, criteria: str = 'price') -> List[Stock]:
        """
        Get Bottom K stocks.
        """
        all_stocks = self.storage.get_all_stocks()
        
        if criteria == 'price':
            return heapq.nsmallest(k, all_stocks, key=lambda s: s.price)
        elif criteria == 'volume':
            return heapq.nsmallest(k, all_stocks, key=lambda s: s.volume)
        else:
            return []

    def get_top_k_stocks_by_sector(self, sector: str, k: int, criteria: str = 'price') -> List[Stock]:
        """
        Get Top K stocks within a specific sector.
        Uses sector_map from storage to get the list, then runs heapq.nlargest.
        """
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

