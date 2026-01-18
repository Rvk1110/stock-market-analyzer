import yfinance as yf
import random

class LiveDataManager:
    def __init__(self):
        # List of popular stocks to track
        self.popular_symbols = [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 
            'JPM', 'V', 'JNJ', 'PFE', 'XOM', 
            'CVX', 'WMT', 'PG', 'NVDA', 'AMD',
            'NFLX', 'DIS', 'KO', 'PEP', 'INTC'
        ]

    def fetch_top_stocks(self):
        """
        Fetches live data for the defined popular symbols.
        Returns a list of dictionaries suited for the Stock model.
        """
        print(f"Fetching live data for {len(self.popular_symbols)} stocks...")
        live_stocks = []
        
        try:
            # Batch fetch is faster
            tickers = yf.Tickers(" ".join(self.popular_symbols))
            
            for symbol in self.popular_symbols:
                try:
                    info = tickers.tickers[symbol].info
                    
                    # Extract Data
                    name = info.get('shortName', symbol)
                    sector = info.get('sector', 'Unknown')
                    price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
                    volume = info.get('averageVolume', 0)
                    
                    # Calculate/Simulate volatility (beta is a good proxy, or randomize)
                    beta = info.get('beta', None)
                    if beta:
                        # Normalize beta roughly to 0-1 for our 'volatility' field (just for demo logic)
                        volatility = min(max(beta / 3, 0.1), 0.99)
                    else:
                        volatility = round(random.uniform(0.1, 0.9), 2)
                        
                    if price and price > 0:
                        stock_data = {
                            "symbol": symbol,
                            "name": name,
                            "sector": sector,
                            "price": float(price),
                            "volume": int(volume),
                            "volatility": float(volatility)
                        }
                        live_stocks.append(stock_data)
                        
                except Exception as inner_e:
                    print(f"Failed to fetch {symbol}: {inner_e}")
                    continue
                    
        except Exception as e:
            print(f"Global fetch error: {e}")
            return []
            
        print(f"Successfully fetched {len(live_stocks)} stocks.")
        return live_stocks

if __name__ == "__main__":
    # simple test
    dm = LiveDataManager()
    data = dm.fetch_top_stocks()
    for d in data[:3]:
        print(d)
