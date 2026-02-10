import random
import time
from typing import List

from models import Stock
from storage import StockStorage
from search import SearchManager
from ranking import RankingManager
from trend_analysis import TrendAnalyzer
from sorting import StockSorter

from live_data import LiveDataManager

def populate_initial_data(storage: StockStorage):
    print("Initializing stock data...")
    
    try:
        dm = LiveDataManager()
        live_stocks = dm.fetch_top_stocks()
        
        if live_stocks:
            print("Using Live Market Data.")
            for s_data in live_stocks:
                stock = Stock(
                    s_data['symbol'], 
                    s_data['name'], 
                    s_data['sector'], 
                    s_data['price'], 
                    s_data['volume'], 
                    s_data['volatility']
                )
                
                stock.price_history = []
                current = stock.price
                for _ in range(10):
                    prev = current / (1 + random.uniform(-0.02, 0.02))
                    stock.price_history.insert(0, prev)
                    current = prev
                stock.price_history.append(stock.price)
                
                storage.add_stock(stock)
            return
            
    except Exception as e:
        print(f"Live data fetch failed: {e}")
        print("Falling back to dummy data.")


    sectors = ['Tech', 'Finance', 'Health', 'Energy', 'Consumer']
    names = {
        'AAPL': 'Apple Inc.', 'GOOGL': 'Alphabet Inc.', 'MSFT': 'Microsoft Corp.',
        'AMZN': 'Amazon.com', 'TSLA': 'Tesla Inc.', 'JPM': 'JPMorgan Chase',
        'V': 'Visa Inc.', 'JNJ': 'Johnson & Johnson', 'PFE': 'Pfizer Inc.',
        'XOM': 'Exxon Mobil', 'CVX': 'Chevron Corp.', 'WMT': 'Walmart Inc.',
        'PG': 'Procter & Gamble', 'NVDA': 'NVIDIA Corp.', 'AMD': 'Advanced Micro Devices'
    }
    
    print("Populating dummy data...")
    for symbol, name in names.items():
        price = round(random.uniform(50, 2000), 2)
        volume = random.randint(10000, 5000000)
        volatility = round(random.uniform(0.1, 0.9), 2)
        sector = random.choice(sectors) 
        
        if symbol in ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'AMD']: sector = 'Tech'
        elif symbol in ['JPM', 'V']: sector = 'Finance'
        elif symbol in ['JNJ', 'PFE']: sector = 'Health'
        elif symbol in ['XOM', 'CVX']: sector = 'Energy'
        
        stock = Stock(symbol, name, sector, price, volume, volatility)
        
        for _ in range(10):
            change = random.uniform(-5, 5)
            stock.update_price(stock.price + change)
            
        storage.add_stock(stock)
    print("Dummy data populated.")

class StockMarketCLI:
    def __init__(self):
        self.storage = StockStorage()
        self.search_manager = SearchManager(self.storage)
        self.ranking_manager = RankingManager(self.storage)
        self.trend_analyzer = TrendAnalyzer()
        self.sorter = StockSorter(threshold=10)

    def print_header(self):
        print("\n==========================================")
        print("    STOCK MARKET ANALYZER (DSA PROJECT)")
        print("==========================================")

    def print_menu(self):
        print("\n1. Add/Update Stock")
        print("2. Search Stock (Symbol/Name/Sector)")
        print("3. View Top K Stocks (Ranking)")
        print("4. Analyze Price Trend (Single Stock)")
        print("5. Sort Stocks (Hybrid Sort)")
        print("6. Show All Stocks")
        print("7. Market Sentiment Analysis (Frequency)")
        print("8. Sector-wise Top K Ranking")
        print("9. Exit")

    def run(self):
        populate_initial_data(self.storage)
        
        while True:
            self.print_header()
            self.print_menu()
            choice = input("\nEnter choice: ")
            
            if choice == '1':
                self.add_update_stock_ui()
            elif choice == '2':
                self.search_stock_ui()
            elif choice == '3':
                self.top_k_ui()
            elif choice == '4':
                self.trend_ui()
            elif choice == '5':
                self.sort_ui()
            elif choice == '6':
                self.show_all_stocks()
            elif choice == '7':
                self.market_sentiment_ui()
            elif choice == '8':
                self.sector_ranking_ui()
            elif choice == '9':
                print("Exiting...")
                break
            else:
                print("Invalid choice!")


    def add_update_stock_ui(self):
        symbol = input("Enter Symbol: ").upper()
        stock = self.storage.get_stock(symbol)
        
        if stock:
            print(f"Stock {symbol} found. Current Price: {stock.price}")
            new_price = float(input("Enter new price: "))
            stock.update_price(new_price)
            print("Price updated successfully!")
        else:
            print("Creating new stock record.")
            name = input("Company Name: ")
            sector = input("Sector: ")
            price = float(input("Price: "))
            volume = int(input("Volume: "))
            volatility = float(input("Volatility (0-1): "))
            
            new_stock = Stock(symbol, name, sector, price, volume, volatility)
            self.storage.add_stock(new_stock)
            print("Stock added successfully!")

    def search_stock_ui(self):
        query = input("Enter search query (Symbol/Name/Sector): ")
        results = self.search_manager.composite_search(query)
        
        if results:
            print(f"\nFound {len(results)} matches:")
            for s in results:
                print(s)
        else:
            print("No matches found.")

    def top_k_ui(self):
        k = int(input("Enter K (how many top stocks): "))
        criteria = input("Criteria (price/volume/score): ")
        
        top_stocks = self.ranking_manager.get_top_k_stocks(k, criteria)
        print(f"\nTop {k} Stocks by {criteria}:")
        for i, s in enumerate(top_stocks, 1):
            score = ""
            if criteria == 'score':
                score = f"(Score: {self.ranking_manager.calculate_priority_score(s):.2f})"
            print(f"{i}. {s} {score}")

    def trend_ui(self):
        symbol = input("Enter Symbol: ").upper()
        stock = self.storage.get_stock(symbol)
        if not stock:
            print("Stock not found!")
            return
            
        trend = self.trend_analyzer.analyze_trend(stock.price_history)
        avg = self.trend_analyzer.calculate_moving_average(stock.price_history)
        
        print(f"\nStock: {stock.name} ({symbol})")
        print(f"Price History: {[round(p, 2) for p in stock.price_history]}")
        print(f"Moving Average (Last 5): {avg:.2f}")
        print(f"Current Trend: {trend}")

    def sort_ui(self):
        key = input("Sort by (price/volume/name/sector): ")
        order = input("Order (asc/desc): ").lower()
        ascending = order == 'asc'
        
        stocks = self.storage.get_all_stocks()
        sorted_stocks = self.sorter.hybrid_sort(stocks, key, ascending)
        
        print(f"\nSorted Stocks by {key} ({order}):")
        for s in sorted_stocks:
            print(s)

    def show_all_stocks(self):
        Sector = input("Filter by sector? (Leave empty for all): ")
        if Sector:
            stocks = self.storage.get_stocks_by_sector(Sector)
        else:
            stocks = self.storage.get_all_stocks()
            
        print(f"\nTotal Stocks: {len(stocks)}")
        for s in stocks:
            print(s)

    def market_sentiment_ui(self):
        stocks = self.storage.get_all_stocks()
        counts = self.trend_analyzer.calculate_market_sentiment(stocks)
        
        print("\n--- Market Sentiment (Stock Behavior Frequency) ---")
        print(f"UP:     {counts['UP']}")
        print(f"DOWN:   {counts['DOWN']}")
        print(f"STABLE: {counts['STABLE']}")
        
        # Simple visualization
        total = len(stocks)
        if total > 0:
            print("\nDistribution:")
            for k, v in counts.items():
                bar = '#' * int((v / total) * 20)
                print(f"{k:6}: {bar} ({v})")

    def sector_ranking_ui(self):
        sector = input("Enter Sector: ")
        k = int(input("Enter K: "))
        criteria = input("Criteria (price/volume/score): ")
        
        top_stocks = self.ranking_manager.get_top_k_stocks_by_sector(sector, k, criteria)
        
        if top_stocks:
            print(f"\nTop {k} Stocks in {sector} by {criteria}:")
            for i, s in enumerate(top_stocks, 1):
                score = ""
                if criteria == 'score':
                    score = f"(Score: {self.ranking_manager.calculate_priority_score(s):.2f})"
                print(f"{i}. {s} {score}")
        else:
            print(f"No stocks found in sector '{sector}'.")


if __name__ == "__main__":
    app = StockMarketCLI()
    app.run()
