from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
from dataclasses import asdict
import random
import threading
import time
import os
from datetime import datetime

# Import existing DSA modules
from models import Stock
from storage import StockStorage
from search import SearchManager
from ranking import RankingManager
from trend_analysis import TrendAnalyzer
from sorting import StockSorter
from sector_analysis import SectorAnalyzer
from main import populate_initial_data # Reuse data population
from live_data import LiveDataManager
from portfolio_manager import PortfolioManager

app = Flask(__name__)
app.secret_key = "rvce_secret_key_1234" # Session encryption

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Global instances (mimicking the persistent state of the CLI app)
storage = StockStorage()
search_manager = SearchManager(storage)
ranking_manager = RankingManager(storage)
trend_analyzer = TrendAnalyzer()
sorter = StockSorter(threshold=20)
sector_analyzer = SectorAnalyzer(storage)
live_data_manager = LiveDataManager()
portfolio_manager = PortfolioManager(storage)

# Track last update time
last_update_time = datetime.now()
data_version = 0

# Initialize data
populate_initial_data(storage)

# Background refresh thread
def background_refresh():
    """Periodically refresh stock data from live sources"""
    global last_update_time, data_version
    while True:
        time.sleep(30)  # Refresh every 30 seconds from yfinance (to avoid rate limits)
        try:
            print("Background refresh: Fetching updated stock data...")
            live_stocks = live_data_manager.fetch_top_stocks()
            
            if live_stocks:
                # Update existing stocks with new prices
                for stock_data in live_stocks:
                    existing_stock = storage.get_stock(stock_data['symbol'])
                    if existing_stock:
                        existing_stock.update_price(stock_data['price'])
                
                last_update_time = datetime.now()
                data_version += 1
                print(f"Background refresh complete. Version: {data_version}")
        except Exception as e:
            print(f"Background refresh error: {e}")

# Start background thread
refresh_thread = threading.Thread(target=background_refresh, daemon=True)
refresh_thread.start()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('market'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == '1234' and password == 'rvce':
            session['logged_in'] = True
            return redirect(url_for('market'))
        else:
            return render_template('login.html', error="Invalid username or password")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('welcome.html', page_id='welcome')

@app.route('/market')
@login_required
def market():
    return render_template('market.html', page_id='market')

@app.route('/stocks')
@login_required
def stocks():
    return render_template('stocks.html', page_id='stocks')

@app.route('/sectors')
@login_required
def sectors():
    return render_template('sectors.html', page_id='sectors')

@app.route('/about')
def about():
    return render_template('about.html', page_id='about')

@app.route('/stock/<symbol>')
@login_required
def stock_detail(symbol):
    stock = storage.get_stock(symbol.upper())
    if not stock:
        return render_template('404.html'), 404 # In a real app
    return render_template('stock_detail.html', stock=stock, page_id='stocks')

@app.route('/api/stocks', methods=['GET'])
@login_required
def get_stocks():
    # Supports sorting via query params
    sort_key = request.args.get('sort', 'price')
    order = request.args.get('order', 'asc')
    ascending = order == 'asc'
    sector_filter = request.args.get('sector', '')
    
    if sector_filter:
        stocks = storage.get_stocks_by_sector(sector_filter)
    else:
        stocks = storage.get_all_stocks()
    
    limit = request.args.get('limit', type=int)
    
    # Use our Hybrid Sort or Scoring
    if sort_key == 'score':
        # Calculate scores and sort
        # We attach score temporarily or just sort by key
        sorted_stocks = sorted(stocks, key=lambda s: ranking_manager.calculate_priority_score(s), reverse=not ascending)
    else:
        sorted_stocks = sorter.hybrid_sort(stocks, sort_key, ascending)
    
    # Apply Limit
    if limit:
        sorted_stocks = sorted_stocks[:limit]
    
    # Prepare response, including score if requested
    response = []
    for s in sorted_stocks:
        s_dict = asdict(s)
        if sort_key == 'score':
            s_dict['score'] = ranking_manager.calculate_priority_score(s)
        response.append(s_dict)

    return jsonify(response)

@app.route('/api/stocks', methods=['POST'])
@login_required
def add_stock():
    data = request.json
    try:
        # Check if exists
        existing = storage.get_stock(data['symbol'])
        if existing:
            # Update price if it's the only field provided or intended
            if 'price' in data:
                existing.update_price(float(data['price']))
                return jsonify({"message": "Stock updated", "stock": asdict(existing)})
        
        # Create new
        new_stock = Stock(
            symbol=data['symbol'],
            name=data['name'],
            sector=data['sector'],
            price=float(data['price']),
            volume=int(data['volume']),
            volatility=float(data['volatility'])
        )
        storage.add_stock(new_stock)
        return jsonify({"message": "Stock created", "stock": asdict(new_stock)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/search')
@login_required
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = search_manager.composite_search(query)
    
    # If no local results, try to fetch live data for the symbol
    if not results:
        print(f"No local match for '{query}', trying live fetch...")
        live_data = live_data_manager.fetch_stock_by_symbol(query)
        if live_data:
            # Create new stock object
            new_stock = Stock(
                symbol=live_data['symbol'],
                name=live_data['name'],
                sector=live_data['sector'],
                price=live_data['price'],
                volume=live_data['volume'],
                volatility=live_data['volatility']
            )
            
            # Add simulated history (copied from main.py logic)
            new_stock.price_history = []
            current = new_stock.price
            for _ in range(10):
                prev = current / (1 + random.uniform(-0.02, 0.02))
                new_stock.price_history.insert(0, prev)
                current = prev
            new_stock.price_history.append(new_stock.price)
            
            # Add to storage
            storage.add_stock(new_stock)
            
            results.append(new_stock)
            
    return jsonify([asdict(s) for s in results])

@app.route('/api/top-k')
@login_required
def get_top_k():
    k = int(request.args.get('k', 5))
    criteria = request.args.get('type', 'price') # price, volume, score
    sector = request.args.get('sector', '')
    
    if sector:
        results = ranking_manager.get_top_k_stocks_by_sector(sector, k, criteria)
    else:
        results = ranking_manager.get_top_k_stocks(k, criteria)
        
    # Serialize and add score if needed for display
    response = []
    for s in results:
        s_dict = asdict(s)
        if criteria == 'score':
            s_dict['score'] = ranking_manager.calculate_priority_score(s)
        response.append(s_dict)
        
    return jsonify(response)

@app.route('/api/sentiment')
@login_required
def get_sentiment():
    stocks = storage.get_all_stocks()
    counts = trend_analyzer.calculate_market_sentiment(stocks)
    return jsonify(counts)

@app.route('/api/sectors')
@login_required
def get_sectors():
    stats = sector_analyzer.calculate_sector_stats()
    return jsonify(stats)


@app.route('/api/last-update')
@login_required
def get_last_update():
    """Return timestamp of last data refresh and version number"""
    return jsonify({
        "last_update": last_update_time.isoformat(),
        "version": data_version,
        "timestamp": last_update_time.strftime("%I:%M:%S %p")
    })

@app.route('/api/trend/<symbol>')
@login_required
def get_trend(symbol):
    stock = storage.get_stock(symbol)
    if not stock:
        return jsonify({"error": "Stock not found"}), 404
        
    trend = trend_analyzer.analyze_trend(stock.price_history)
    sma = trend_analyzer.calculate_moving_average(stock.price_history)
    return jsonify({
        "symbol": symbol,
        "trend": trend,
        "sma": sma,
        "history": stock.price_history,
        "priority_score": ranking_manager.calculate_priority_score(stock)
    })

# --- Portfolio Routes ---

@app.route('/portfolio')
@login_required
def portfolio():
    return render_template('portfolio.html', page_id='portfolio')

@app.route('/api/portfolio/add', methods=['POST'])
@login_required
def add_portfolio_item():
    data = request.json
    try:
        success = portfolio_manager.add_stock(
            data['symbol'],
            int(data['quantity']),
            float(data['buy_price']),
            data['platform']
        )
        if success:
            return jsonify({"message": "Stock added to portfolio"})
        else:
            return jsonify({"error": "Invalid Stock Symbol"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/portfolio/stats')
@login_required
def get_portfolio_stats():
    stats = portfolio_manager.get_portfolio_stats()
    stats['health_score'] = portfolio_manager.calculate_portfolio_health_score()
    return jsonify(stats)

@app.route('/api/portfolio/holdings')
@login_required
def get_portfolio_holdings():
    sort_key = request.args.get('sort', 'profit')
    ascending = request.args.get('order', 'desc') == 'asc'
    return jsonify(portfolio_manager.get_all_holdings_sorted(sort_key, ascending))

@app.route('/api/portfolio/top-k')
@login_required
def get_portfolio_top_k():
    k = int(request.args.get('k', 3))
    criteria = request.args.get('type', 'profit')
    return jsonify(portfolio_manager.get_top_k_holdings(k, criteria))

@app.route('/api/portfolio/distribution')
@login_required
def get_portfolio_distribution():
    return jsonify(portfolio_manager.get_platform_distribution())

@app.route('/api/portfolio/scatter')
@login_required
def get_portfolio_scatter():
    return jsonify(portfolio_manager.get_risk_vs_profit_data())

@app.route('/api/portfolio/sectors')
@login_required
def get_portfolio_sectors():
    return jsonify(portfolio_manager.get_sector_distribution())


if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("\n" + "="*60)
        print("  🚀 STOCK MARKET ANALYZER DASHBOARD IS LIVE!")
        print("  🔗 Open your dashboard at: http://localhost:5001")
        print("="*60 + "\n")
    app.run(debug=True, port=5001, host='0.0.0.0')
