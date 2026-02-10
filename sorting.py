from typing import List, Callable
from models import Stock

class StockSorter:
    def __init__(self, threshold: int = 50):
        self.threshold = threshold

    def _quick_sort(self, stocks: List[Stock], key_func: Callable[[Stock], float]) -> List[Stock]:
        if len(stocks) <= 1:
            return stocks
        
        pivot = stocks[len(stocks) // 2]
        pivot_val = key_func(pivot)
        
        left = [x for x in stocks if key_func(x) < pivot_val]
        middle = [x for x in stocks if key_func(x) == pivot_val]
        right = [x for x in stocks if key_func(x) > pivot_val]
        
        return self._quick_sort(left, key_func) + middle + self._quick_sort(right, key_func)

    def _merge_sort(self, stocks: List[Stock], key_func: Callable[[Stock], float]) -> List[Stock]:
        if len(stocks) <= 1:
            return stocks

        mid = len(stocks) // 2
        left = self._merge_sort(stocks[:mid], key_func)
        right = self._merge_sort(stocks[mid:], key_func)

        return self._merge(left, right, key_func)

    def _merge(self, left: List[Stock], right: List[Stock], key_func: Callable) -> List[Stock]:
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if key_func(left[i]) <= key_func(right[j]):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
                
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def hybrid_sort(self, stocks: List[Stock], key: str = 'price', ascending: bool = True) -> List[Stock]:
        key_map = {
            'price': lambda s: s.price,
            'volume': lambda s: s.volume,
            'sector': lambda s: s.sector,
            'name': lambda s: s.name,
        }
        
        key_func = key_map.get(key, lambda s: s.price)
        
        if len(stocks) < self.threshold:
            sorted_stocks = self._quick_sort(stocks, key_func)
        else:
            sorted_stocks = self._merge_sort(stocks, key_func)
            
        if not ascending:
            return sorted_stocks[::-1]
            
        return sorted_stocks
