from typing import List, Dict, Any, Tuple
import heapq
from dataclasses import dataclass, asdict
from collections import defaultdict
from models import Stock

@dataclass
class PortfolioItem:
    symbol: str
    quantity: int
    buy_price: float
    platform: str
    current_price: float = 0.0
    current_value: float = 0.0
    profit_loss: float = 0.0
    profit_loss_pct: float = 0.0
    volatility: float = 0.0 # From main stock data
    sector: str = "" # From main stock data

class PortfolioManager:
    def __init__(self, storage):
        """
        Initialize Portfolio Manager.
        Storage: Hash Map (Dictionary) for O(1) access to portfolio items.
        Platform Tracking: Set for O(1) uniqueness check.
        """
        self.storage = storage # Reference to main StockStorage to get real-time price/volatility
        self.holdings: Dict[str, PortfolioItem] = {} # Key: Symbol
        self.platforms = set()

    def add_stock(self, symbol: str, quantity: int, buy_price: float, platform: str) -> bool:
        """
        Add or Update a stock in the portfolio.
        Time Complexity: O(1) average case (Hash Map put).
        """
        symbol = symbol.upper()
        
        # Check if stock exists in main storage (to validate symbol)
        stock_data = self.storage.get_stock(symbol)
        if not stock_data:
            return False # or raise error

        # Update Platform Set (O(1))
        self.platforms.add(platform)

        # Update Holdings (Hash Map O(1))
        if symbol in self.holdings:
            # Update existing holding (Weighted Average Price logic could be added, but keeping simple for now)
            # For this version, we'll just update quantity and avg buy price if user adds more
            existing = self.holdings[symbol]
            total_cost = (existing.quantity * existing.buy_price) + (quantity * buy_price)
            total_qty = existing.quantity + quantity
            avg_price = total_cost / total_qty
            
            existing.quantity = total_qty
            existing.buy_price = avg_price
            existing.platform = platform # Update platform to latest
        else:
            self.holdings[symbol] = PortfolioItem(
                symbol=symbol,
                quantity=quantity,
                buy_price=buy_price,
                platform=platform
            )
        return True

    def _update_market_data(self):
        """
        Internal helper to sync holdings with latest market data.
        Time Complexity: O(N) where N is number of holdings.
        """
        for symbol, item in self.holdings.items():
            stock = self.storage.get_stock(symbol)
            if stock:
                item.current_price = stock.price
                item.current_value = item.quantity * stock.price
                item.profit_loss = item.current_value - (item.quantity * item.buy_price)
                if item.buy_price > 0:
                    item.profit_loss_pct = (item.profit_loss / (item.quantity * item.buy_price)) * 100
                item.volatility = stock.volatility
                item.sector = stock.sector

    def get_portfolio_stats(self) -> Dict[str, Any]:
        """
        Calculate aggregate portfolio statistics.
        Time Complexity: O(N) linear scan.
        """
        self._update_market_data()
        
        total_investment = 0.0
        current_value = 0.0
        total_pl = 0.0
        
        for item in self.holdings.values():
            total_investment += item.quantity * item.buy_price
            current_value += item.current_value
            total_pl += item.profit_loss
            
        return {
            "total_investment": total_investment,
            "current_value": current_value,
            "total_pl": total_pl,
            "total_pl_pct": (total_pl / total_investment * 100) if total_investment > 0 else 0,
            "platform_count": len(self.platforms)
        }

    def get_platform_distribution(self) -> Dict[str, float]:
        """
        Get value distribution by platform.
        Time Complexity: O(N).
        """
        dist = defaultdict(float)
        for item in self.holdings.values():
            dist[item.platform] += item.current_value
        return dict(dist)

    def get_sector_distribution(self) -> Dict[str, float]:
        """
        Get value distribution by sector.
        Time Complexity: O(N).
        """
        self._update_market_data()
        dist = defaultdict(float)
        for item in self.holdings.values():
            dist[item.sector] += item.current_value
        return dict(dist)

    def get_top_k_holdings(self, k: int, criteria: str = 'profit') -> List[Dict]:
        """
        Get Top K holdings using Heap.
        Time Complexity: O(N + K log N) using heapq.nlargest.
        Criteria: 'profit', 'risk' (volatility), 'score' (composite).
        """
        self._update_market_data()
        items = list(self.holdings.values())
        
        if not items:
            return []

        if criteria == 'profit':
            # Max Heap for Profit
            top_k = heapq.nlargest(k, items, key=lambda x: x.profit_loss)
        elif criteria == 'risk':
            # Max Heap for Volatility (Highest Risk)
            top_k = heapq.nlargest(k, items, key=lambda x: x.volatility)
        elif criteria == 'score':
             # Max Heap for Composite Score
            top_k = heapq.nlargest(k, items, key=lambda x: self._calculate_item_score(x))
        else:
            return []
            
        return [asdict(item) for item in top_k]

    def _calculate_item_score(self, item: PortfolioItem) -> float:
        """
        Deterministic Score for a single holding.
        Higher is better.
        Logic: (Profit% * 0.5) + (Stability * 20) - (High Volatility Penalty)
        """
        volatility_penalty = item.volatility * 100
        # simple stability: 1/volatility if vol > 0
        stability_score = (1 / item.volatility) if item.volatility > 0.01 else 50
        
        score = (item.profit_loss_pct * 0.5) + (stability_score * 0.2)
        return score

    def calculate_portfolio_health_score(self) -> float:
        """
        Deterministic Portfolio Health Score (0-100).
        Factors:
        1. Profitability (Max 40 pts)
        2. Diversification (Max 20 pts)
        3. Risk Management (Max 40 pts)
        """
        stats = self.get_portfolio_stats()
        
        # 1. Profitability Score
        # If P/L% is > 20%, max points. If < -20%, 0 points. Linear scale.
        pl_pct = stats['total_pl_pct']
        profit_score = min(40, max(0, 20 + pl_pct)) # 20 is baseline (0% gain)
        
        # 2. Diversification Score
        # 1 platform = 5pts, 2 = 10pts, 3+ = 20pts
        platform_count = stats['platform_count']
        diversity_score = min(20, platform_count * 7) # Cap at 20
        
        # 3. Risk Score ( Inverse of Average Volatility )
        total_vol = sum(self.holdings[s].volatility for s in self.holdings)
        avg_vol = total_vol / len(self.holdings) if self.holdings else 1.0
        # Lower vol is better. If vol < 1.0, good.
        risk_score = max(0, 40 - (avg_vol * 20))
        
        total_score = profit_score + diversity_score + risk_score
        return min(100, round(total_score, 1))

    def get_all_holdings_sorted(self, sort_key='profit', ascending=False) -> List[Dict]:
        """
        Returns full list of holdings sorted by key.
        Uses Python's Timsort (Hybrid Sort).
        """
        self._update_market_data()
        items = list(self.holdings.values())
        
        key_map = {
            'symbol': lambda x: x.symbol,
            'avg_price': lambda x: x.buy_price,
            'price': lambda x: x.current_price,
            'profit': lambda x: x.profit_loss,
            'volatility': lambda x: x.volatility,
            'platform': lambda x: x.platform,
            'score': lambda x: self._calculate_item_score(x)
        }
        
        key_func = key_map.get(sort_key, lambda x: x.profit_loss)
        
        sorted_items = sorted(items, key=key_func, reverse=not ascending)
        
        # Attach individual scores to result
        results = []
        for item in sorted_items:
            d = asdict(item)
            d['score'] = round(self._calculate_item_score(item), 2)
            results.append(d)
            
        return results

    def get_risk_vs_profit_data(self) -> List[Dict]:
        """
        Data for Scatter Plot: X=Volatility, Y=Profit%
        """
        self._update_market_data()
        data = []
        for item in self.holdings.values():
            data.append({
                'x': item.volatility,
                'y': item.profit_loss_pct,
                'r': 5 + (item.current_value / 1000) # Radius based on position size (scaled)
            })
        return data
