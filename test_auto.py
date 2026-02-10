import unittest
from models import Stock
from storage import StockStorage
from search import SearchManager
from ranking import RankingManager
from trend_analysis import TrendAnalyzer
from sorting import StockSorter
from sector_analysis import SectorAnalyzer

class TestStockMarketAnalyzer(unittest.TestCase):
    def setUp(self):
        self.storage = StockStorage()
        self.search = SearchManager(self.storage)
        self.ranking = RankingManager(self.storage)
        self.trend = TrendAnalyzer()
        self.sorter = StockSorter(threshold=5)
        self.sector = SectorAnalyzer(self.storage)


        self.s1 = Stock("AAPL", "Apple", "Tech", 150.0, 1000, 0.2)
        self.s2 = Stock("GOOG", "Google", "Tech", 2000.0, 500, 0.3)
        self.s3 = Stock("TSLA", "Tesla", "Auto", 700.0, 2000, 0.8)
        self.s4 = Stock("AMZN", "Amazon", "Tech", 3000.0, 800, 0.4)
        self.s5 = Stock("MSFT", "Microsoft", "Tech", 250.0, 1200, 0.25)
        self.s6 = Stock("NVDA", "Nvidia", "Tech", 600.0, 1500, 0.6)

        self.storage.add_stock(self.s1)
        self.storage.add_stock(self.s2)
        self.storage.add_stock(self.s3)
        self.storage.add_stock(self.s4)
        self.storage.add_stock(self.s5)
        self.storage.add_stock(self.s6)

    def test_storage(self):
        self.assertEqual(self.storage.get_stock("AAPL"), self.s1)
        self.assertIsNone(self.storage.get_stock("INVALID"))
        self.assertEqual(len(self.storage.get_stocks_by_sector("Tech")), 5)
        self.assertEqual(len(self.storage.get_stocks_by_sector("Auto")), 1)

    def test_search(self):
        res = self.search.search_by_name("App")
        self.assertIn(self.s1, res)
        res_comp = self.search.composite_search("Tech")
        self.assertEqual(len(res_comp), 5) 
        res_comp_sym = self.search.composite_search("TSLA")
        self.assertIn(self.s3, res_comp_sym)

    def test_ranking(self):
        top = self.ranking.get_top_k_stocks(1, 'price')
        self.assertEqual(top[0].symbol, "AMZN")


        top_vol = self.ranking.get_top_k_stocks(1, 'volume')
        self.assertEqual(top_vol[0].symbol, "TSLA")

    def test_trend(self):
        prices = [100.0, 101.0, 102.0, 103.0, 104.0]
        trend = self.trend.analyze_trend(prices)
        self.assertEqual(trend, "UP")
        
        prices_down = [100.0, 99.0, 98.0, 97.0, 96.0] 
        trend_down = self.trend.analyze_trend(prices_down)
        self.assertEqual(trend_down, "DOWN")

    def test_sorting(self):
        sorted_stocks = self.sorter.hybrid_sort(self.storage.get_all_stocks(), 'price', True)
        self.assertEqual(sorted_stocks[0].symbol, "AAPL")
        self.assertEqual(sorted_stocks[-1].symbol, "AMZN")

        small_list = [self.s2, self.s1]
        sorted_small = self.sorter.hybrid_sort(small_list, 'price', True)
        self.assertEqual(sorted_small[0].symbol, "AAPL")

    def test_market_sentiment(self):
        self.s1.price_history = [150.0, 150.0, 150.0]
        self.s2.price_history = [2000.0, 2010.0, 2020.0, 2050.0]
        self.s3.price_history = [700.0, 690.0, 680.0, 650.0] # DOWN

        stocks = [self.s1, self.s2, self.s3]
        counts = self.trend.calculate_market_sentiment(stocks)
        self.assertIn("UP", counts)
        self.assertIn("DOWN", counts)
        self.assertIn("STABLE", counts)
    
    def test_sector_ranking(self):
        top_tech = self.ranking.get_top_k_stocks_by_sector("Tech", 1, 'price')
        self.assertEqual(top_tech[0].symbol, "AMZN")
        
        top_tech_vol = self.ranking.get_top_k_stocks_by_sector("Tech", 1, 'volume')
        self.assertEqual(top_tech_vol[0].symbol, "NVDA")
    def test_sector_analysis(self):
        stats = self.sector.calculate_sector_stats()
        
        self.assertEqual(len(stats), 2)
        
        tech_stat = next(s for s in stats if s['sector'] == 'Tech')
        self.assertEqual(tech_stat['count'], 5)
        self.assertAlmostEqual(tech_stat['avg_price'], 1200.0, places=1)
        
        auto_stat = next(s for s in stats if s['sector'] == 'Auto')
        self.assertEqual(auto_stat['count'], 1)
        self.assertEqual(auto_stat['avg_price'], 700.0)


if __name__ == '__main__':
    unittest.main()

