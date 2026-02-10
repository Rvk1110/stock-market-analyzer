import yfinance as yf
import random

class LiveDataManager:
    def __init__(self):
        self.popular_symbols = [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 
            'JPM', 'V', 'JNJ', 'PFE', 'XOM', 
            'CVX', 'WMT', 'PG', 'NVDA', 'AMD',
            'NFLX', 'DIS', 'KO', 'PEP', 'INTC'
        ]

    def fetch_top_stocks(self):
        print(f"Fetching live data for {len(self.popular_symbols)} stocks...")
        live_stocks = []
        
        try:
            tickers = yf.Tickers(" ".join(self.popular_symbols))
            
            for symbol in self.popular_symbols:
                try:
                    info = tickers.tickers[symbol].info
                    
                    name = info.get('shortName', symbol)
                    sector = info.get('sector', 'Unknown')
                    price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
                    volume = info.get('averageVolume', 0)
                    
                    beta = info.get('beta', None)
                    if beta:
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

    def fetch_stock_by_symbol(self, symbol: str):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if 'symbol' not in info and 'shortName' not in info:
                 if 'regularMarketPrice' not in info:
                     return None

            price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
            if not price: return None

            stock_data = {
                "symbol": info.get('symbol', symbol).upper(),
                "name": info.get('shortName', symbol),
                "sector": info.get('sector', 'Unknown'),
                "price": float(price),
                "volume": int(info.get('averageVolume', 0)),
                "volatility": 0.5
            }
            
            beta = info.get('beta', None)
            if beta:
                stock_data['volatility'] = min(max(beta / 3, 0.1), 0.99)
            
            return stock_data
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

if __name__ == "__main__":
    dm = LiveDataManager()
    data = dm.fetch_top_stocks()
    for d in data[:3]:
        print(d)
