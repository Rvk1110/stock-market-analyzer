from typing import List, Dict
from models import Stock
from storage import StockStorage

class SectorAnalyzer:
    def __init__(self, storage: StockStorage):
        self.storage = storage

    def calculate_sector_stats(self) -> List[Dict]:
        """
        Aggregates performance metrics by sector.
        
        Algorithm:
        1. Iterate through sector_map (Hash Map Traversal).
        2. For each sector, iterate its stocks (List Traversal).
        3. Compute aggregates (Sum Price, Sum Volume).
        4. Calculate averages.
        
        Time Complexity: O(N) where N is total stocks.
        """
        sector_stats = []
        
        # O(S) where S is number of sectors
        for sector, stocks in self.storage.sector_map.items():
            if not stocks:
                continue
                
            total_price = 0.0
            total_volume = 0
            total_volatility = 0.0
            count = len(stocks)
            
            # O(M) where M is stocks in that sector
            for stock in stocks:
                total_price += stock.price
                total_volume += stock.volume
                total_volatility += stock.volatility
                
            avg_price = total_price / count
            avg_volatility = total_volatility / count
            
            sector_stats.append({
                "sector": sector,
                "count": count,
                "avg_price": round(avg_price, 2),
                "avg_volatility": round(avg_volatility, 3),
                "total_volume": total_volume
            })
            
        # Optional: Sort by Avg Price descending for better UI
        # Using Python's Timsort (O(S log S))
        sector_stats.sort(key=lambda x: x['avg_price'], reverse=True)
            
        return sector_stats
