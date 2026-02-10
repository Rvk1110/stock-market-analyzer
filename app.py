from flask import Flask, render_template, jsonify, request
from dataclasses import asdict
import random
import threading
import time
import os
from datetime import datetime

from models import Stock
from storage import StockStorage
from search import SearchManager
from ranking import RankingManager
from trend_analysis import TrendAnalyzer
from sorting import StockSorter
from sector_analysis import SectorAnalyzer
from main import populate_initial_data # Reuse data population
from live_data import LiveDataManager

app = Flask(__name__)

storage = StockStorage()
search_manager = SearchManager(storage)
ranking_manager = RankingManager(storage)
trend_analyzer = TrendAnalyzer()
sorter = StockSorter(threshold=20)
sector_analyzer = SectorAnalyzer(storage)
live_data_manager = LiveDataManager()

last_update_time = datetime.now()
data_version = 0

populate_initial_data(storage)

def background_refresh():
    global last_update_time, data_version
    while True:
        time.sleep(30)
        try:
            print("Background refresh: Fetching updated stock data...")
            live_stocks = live_data_manager.fetch_top_stocks()
            
            if live_stocks:

                for stock_data in live_stocks:
                    existing_stock = storage.get_stock(stock_data['symbol'])
                    if existing_stock:
                        existing_stock.update_price(stock_data['price'])
                
                last_update_time = datetime.now()
                data_version += 1
                print(f"Background refresh complete. Version: {data_version}")
        except Exception as e:
            print(f"Background refresh error: {e}")

refresh_thread = threading.Thread(target=background_refresh, daemon=True)
refresh_thread.start()


@app.route('/')
def index():
    return render_template('welcome.html', page_id='welcome')

@app.route('/market')
def market():
    return render_template('market.html', page_id='market')

@app.route('/stocks')
def stocks():
    return render_template('stocks.html', page_id='stocks')

@app.route('/sectors')
def sectors():
    return render_template('sectors.html', page_id='sectors')

@app.route('/about')
def about():
    return render_template('about.html', page_id='about')

@app.route('/stock/<symbol>')
def stock_detail(symbol):
    stock = storage.get_stock(symbol.upper())
    if not stock:
        return render_template('404.html'), 404
    return render_template('stock_detail.html', stock=stock, page_id='stocks')

@app.route('/api/stocks', methods=['GET'])
def get_stocks():

    sort_key = request.args.get('sort', 'price')
    order = request.args.get('order', 'asc')
    ascending = order == 'asc'
    sector_filter = request.args.get('sector', '')
    
    if sector_filter:
        stocks = storage.get_stocks_by_sector(sector_filter)
    else:
        stocks = storage.get_all_stocks()
    
    limit = request.args.get('limit', type=int)
    
    if sort_key == 'score':
        sorted_stocks = sorted(stocks, key=lambda s: ranking_manager.calculate_priority_score(s), reverse=not ascending)
    else:
        sorted_stocks = sorter.hybrid_sort(stocks, sort_key, ascending)
    

    if limit:
        sorted_stocks = sorted_stocks[:limit]
    

    response = []
    for s in sorted_stocks:
        s_dict = asdict(s)
        if sort_key == 'score':
            s_dict['score'] = ranking_manager.calculate_priority_score(s)
        response.append(s_dict)

    return jsonify(response)

@app.route('/api/stocks', methods=['POST'])
def add_stock():
    data = request.json
    try:
        existing = storage.get_stock(data['symbol'])
        if existing:
            if 'price' in data:
                existing.update_price(float(data['price']))
                return jsonify({"message": "Stock updated", "stock": asdict(existing)})
        
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
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = search_manager.composite_search(query)
    

    if not results:
        print(f"No local match for '{query}', trying live fetch...")
        live_data = live_data_manager.fetch_stock_by_symbol(query)
        if live_data:

            new_stock = Stock(
                symbol=live_data['symbol'],
                name=live_data['name'],
                sector=live_data['sector'],
                price=live_data['price'],
                volume=live_data['volume'],
                volatility=live_data['volatility']
            )
            
            new_stock.price_history = []
            current = new_stock.price
            for _ in range(10):
                prev = current / (1 + random.uniform(-0.02, 0.02))
                new_stock.price_history.insert(0, prev)
                current = prev
            new_stock.price_history.append(new_stock.price)
            
            storage.add_stock(new_stock)
            
            results.append(new_stock)
            
    return jsonify([asdict(s) for s in results])

@app.route('/api/top-k')
def get_top_k():
    k = int(request.args.get('k', 5))
    criteria = request.args.get('type', 'price')
    sector = request.args.get('sector', '')
    
    if sector:
        results = ranking_manager.get_top_k_stocks_by_sector(sector, k, criteria)
    else:
        results = ranking_manager.get_top_k_stocks(k, criteria)
        
    response = []
    for s in results:
        s_dict = asdict(s)
        if criteria == 'score':
            s_dict['score'] = ranking_manager.calculate_priority_score(s)
        response.append(s_dict)
        
    return jsonify(response)

@app.route('/api/sentiment')
def get_sentiment():
    stocks = storage.get_all_stocks()
    counts = trend_analyzer.calculate_market_sentiment(stocks)
    return jsonify(counts)

@app.route('/api/sectors')
def get_sectors():
    stats = sector_analyzer.calculate_sector_stats()
    return jsonify(stats)


@app.route('/api/last-update')
def get_last_update():
    return jsonify({
        "last_update": last_update_time.isoformat(),
        "version": data_version,
        "timestamp": last_update_time.strftime("%I:%M:%S %p")
    })

@app.route('/api/trend/<symbol>')
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
        "history": stock.price_history
    })

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("\n" + "="*60)
        print("  🚀 STOCK MARKET ANALYZER DASHBOARD IS LIVE!")
        print("  🔗 Open your dashboard at: http://localhost:5001")
        print("="*60 + "\n")
    app.run(debug=True, port=5001, host='0.0.0.0')
