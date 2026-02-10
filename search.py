from typing import List
from models import Stock
from storage import StockStorage

class SearchManager:
    def __init__(self, storage: StockStorage):
        self.storage = storage

    def search_by_name(self, query: str) -> List[Stock]:
        query = query.lower()
        results = []
        for stock in self.storage.get_all_stocks():
            if query in stock.name.lower():
                results.append(stock)
        return results

    def search_by_symbol(self, query: str) -> List[Stock]:
        query = query.upper()
        results = []
        for stock in self.storage.get_all_stocks():
            if query in stock.symbol:
                results.append(stock)
        return results

    def composite_search(self, query: str) -> List[Stock]:
        query_lower = query.lower()
        results = []
        seen_symbols = set()
        
        for stock in self.storage.get_all_stocks():
            if (query_lower in stock.symbol.lower() or 
                query_lower in stock.name.lower() or 
                query_lower in stock.sector.lower()):
                
                if stock.symbol not in seen_symbols:
                    results.append(stock)
                    seen_symbols.add(stock.symbol)
        
        return results
