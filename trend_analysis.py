from collections import deque
from typing import List

class TrendAnalyzer:
    def __init__(self, window_size: int = 5):
        self.window_size = window_size

    def calculate_moving_average(self, prices: List[float]) -> float:
        """
        Calculates Simple Moving Average (SMA) using the last N prices.
        Uses a sliding window approach.
        Time Complexity: O(K) where K is window size (or O(1) if maintained iteratively).
        Here we slice list which is O(K).
        """
        if not prices:
            return 0.0
        
        # Use deque for efficient sliding window simulation
        # Since deque doesn't support slicing directly, we convert to list
        # This is O(K) where K is window size (small), so it's acceptable.
        recent_prices = list(prices)[-self.window_size:]
        if not recent_prices:
            return 0.0
        return sum(recent_prices) / len(recent_prices)

    def analyze_trend(self, prices: List[float]) -> str:
        """
        Determines if trend is UP, DOWN, or STABLE based on SMA vs Current Price.
        """
        if len(prices) < 2:
            return "STABLE"

        sma = self.calculate_moving_average(prices)
        current_price = prices[-1] # Deque supports index -1 access

        # Simple threshold for stability (e.g. within 0.5% diff)
        threshold = sma * 0.005
        
        if current_price > sma + threshold:
            return "UP"
        elif current_price < sma - threshold:
            return "DOWN"
        else:
            return "STABLE"

    def calculate_market_sentiment(self, stocks: List['Stock']) -> dict:
        """
        Tracks frequency of stock behavior (UP/DOWN/STABLE) using a dictionary.
        Time Complexity: O(N * K) where N is stocks and K is window size.
        """
        sentiment_counts = {"UP": 0, "DOWN": 0, "STABLE": 0}
        
        for stock in stocks:
            trend = self.analyze_trend(stock.price_history)
            if trend in sentiment_counts:
                sentiment_counts[trend] += 1
                
        return sentiment_counts

