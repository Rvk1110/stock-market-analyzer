from collections import deque
from typing import List

class TrendAnalyzer:
    def __init__(self, window_size: int = 5):
        self.window_size = window_size

    def calculate_moving_average(self, prices: List[float]) -> float:
        if not prices:
            return 0.0
        
        recent_prices = list(prices)[-self.window_size:]
        if not recent_prices:
            return 0.0
        return sum(recent_prices) / len(recent_prices)

    def analyze_trend(self, prices: List[float]) -> str:
        if len(prices) < 2:
            return "STABLE"

        sma = self.calculate_moving_average(prices)
        current_price = prices[-1]

        threshold = sma * 0.005
        
        if current_price > sma + threshold:
            return "UP"
        elif current_price < sma - threshold:
            return "DOWN"
        else:
            return "STABLE"

    def calculate_market_sentiment(self, stocks: List['Stock']) -> dict:
        sentiment_counts = {"UP": 0, "DOWN": 0, "STABLE": 0}
        
        for stock in stocks:
            trend = self.analyze_trend(stock.price_history)
            if trend in sentiment_counts:
                sentiment_counts[trend] += 1
                
        return sentiment_counts

