from flask import Flask, render_template, jsonify, request
from dataclasses import asdict
import random

# Import existing DSA modules
from models import Stock
from storage import StockStorage
from search import SearchManager
from ranking import RankingManager
from trend_analysis import TrendAnalyzer
from sorting import StockSorter
from sector_analysis import SectorAnalyzer
from main import populate_dummy_data # Reuse dummy data generation

app = Flask(__name__)

# Global instances (mimicking the persistent state of the CLI app)
storage = StockStorage()
search_manager = SearchManager(storage)
ranking_manager = RankingManager(storage)
trend_analyzer = TrendAnalyzer()
sorter = StockSorter(threshold=20)
sector_analyzer = SectorAnalyzer(storage)

# Initialize data
populate_dummy_data(storage)

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

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    # Supports sorting via query params
    sort_key = request.args.get('sort', 'price')
    order = request.args.get('order', 'asc')
    ascending = order == 'asc'
    
    stocks = storage.get_all_stocks()
    
    # Use our Hybrid Sort
    sorted_stocks = sorter.hybrid_sort(stocks, sort_key, ascending)
    
    return jsonify([asdict(s) for s in sorted_stocks])

@app.route('/api/stocks', methods=['POST'])
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
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = search_manager.composite_search(query)
    return jsonify([asdict(s) for s in results])

@app.route('/api/top-k')
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
def get_sentiment():
    stocks = storage.get_all_stocks()
    counts = trend_analyzer.calculate_market_sentiment(stocks)
    return jsonify(counts)

@app.route('/api/sectors')
def get_sectors():
    stats = sector_analyzer.calculate_sector_stats()
    return jsonify(stats)

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
    app.run(debug=True, port=5001, host='0.0.0.0')
