# 📚 VIVA Q&A GUIDE - Stock Market Analyzer (DSA Project)

## 🎯 Project Overview Questions

### Q1: What is your project about?
**Answer:**
My project is a **Stock Market Analyzer** that demonstrates various Data Structures and Algorithms concepts through a real-world application. It allows users to:
- Add/update stocks with live data integration
- Search stocks efficiently using hash tables
- Rank stocks using heap-based algorithms
- Analyze price trends using sliding window techniques
- Sort stocks using hybrid sorting algorithms
- Perform sector-wise analysis

The project has both a **CLI interface** (`main.py`) and a **web dashboard** (`app.py`) with real-time data updates.

---

### Q2: Why did you choose this project?
**Answer:**
I chose this project because:
1. **Real-world relevance** - Stock market analysis is a practical application
2. **Multiple DSA concepts** - Allows demonstration of various data structures and algorithms
3. **Performance optimization** - Shows understanding of time/space complexity tradeoffs
4. **Scalability** - Designed to handle large datasets efficiently
5. **Live data integration** - Demonstrates API integration and background processing

---

## 🏗️ Data Structures Questions

### Q3: What data structures did you use and why?

**Answer:**
I used **three primary data structures** in `storage.py`:

1. **Hash Table (Dictionary) - `stocks_map`**
   - **Purpose:** O(1) stock lookup by symbol
   - **Why:** Instant access when searching by symbol
   - **Time Complexity:** O(1) average case

2. **Dynamic Array (List) - `stocks_list`**
   - **Purpose:** Sequential access to all stocks
   - **Why:** Needed for iteration, sorting, and maintaining insertion order
   - **Time Complexity:** O(1) append, O(N) search

3. **Inverted Index (Dictionary of Lists) - `sector_map`**
   - **Purpose:** Group stocks by sector
   - **Why:** O(1) sector filtering instead of O(N) linear scan
   - **Time Complexity:** O(1) sector lookup

**Tradeoff:** I used redundant storage (same stock in multiple structures) to optimize query performance - trading space for time.

---

### Q4: Why did you use a hash table instead of a list for stock lookup?

**Answer:**
**Hash Table (Dictionary):**
- **Lookup:** O(1) average case
- **Example:** Finding "AAPL" among 10,000 stocks = 1 operation

**List:**
- **Lookup:** O(N) linear search
- **Example:** Finding "AAPL" among 10,000 stocks = up to 10,000 comparisons

For a stock market analyzer where users frequently search by symbol, **O(1) lookup is critical** for performance. Hash tables provide instant access using the symbol as the key.

---

### Q5: Explain the heap data structure used in your project.

**Answer:**
I used **heaps** for the **Top K problem** in `ranking.py`:

```python
heapq.nlargest(k, all_stocks, key=lambda s: s.price)
```

**How it works:**
- A heap is a **binary tree** where parent nodes are larger (max heap) or smaller (min heap) than children
- `heapq.nlargest()` uses a **min heap of size K**
- As we iterate through N stocks, we maintain only the K largest

**Time Complexity:**
- **Heap approach:** O(N log K)
- **Full sort approach:** O(N log N)

**Why better:** When K << N (e.g., top 5 from 10,000 stocks), heap is much faster.

**Example:** Finding top 5 from 10,000 stocks:
- Heap: ~10,000 × log(5) = ~23,000 operations
- Sort: ~10,000 × log(10,000) = ~133,000 operations

---

## ⚙️ Algorithm Questions

### Q6: Explain your hybrid sorting algorithm.

**Answer:**
My hybrid sort in `sorting.py` **adaptively chooses** between Quick Sort and Merge Sort based on dataset size:

```python
if len(stocks) < self.threshold:
    sorted_stocks = self._quick_sort(stocks, key_func)
else:
    sorted_stocks = self._merge_sort(stocks, key_func)
```

**Quick Sort (Small datasets):**
- **Time:** O(N log N) average, O(N²) worst
- **Space:** O(log N) - in-place
- **Advantage:** Faster for small data due to cache efficiency, lower overhead

**Merge Sort (Large datasets):**
- **Time:** O(N log N) guaranteed
- **Space:** O(N) - requires extra memory
- **Advantage:** Stable, predictable performance, no worst case

**Threshold:** Set to 10 (configurable)

**Why hybrid?** Combines strengths of both - speed for small data, reliability for large data.

---

### Q7: What is the time complexity of your search operation?

**Answer:**
I have **three search methods** in `search.py`:

1. **Exact Symbol Search (using hash table):**
   - **Method:** `storage.get_stock(symbol)`
   - **Complexity:** O(1)
   - **Why:** Direct hash table lookup

2. **Partial Symbol Search:**
   - **Method:** `search_by_symbol(query)`
   - **Complexity:** O(N × M) where N = stocks, M = symbol length
   - **Why:** Must scan all stocks for substring match

3. **Composite Search (Symbol OR Name OR Sector):**
   - **Method:** `composite_search(query)`
   - **Complexity:** O(N × L) where L = average string length
   - **Why:** Checks three fields per stock
   - **Optimization:** Uses a set to avoid duplicates (O(1) membership check)

**Could be improved with:** Trie data structure for prefix matching or inverted index for full-text search.

---

### Q8: Explain the moving average algorithm.

**Answer:**
I use a **sliding window** approach in `trend_analysis.py`:

```python
def calculate_moving_average(self, prices: List[float]) -> float:
    recent_prices = prices[-self.window_size:]
    return sum(recent_prices) / len(recent_prices)
```

**Algorithm:**
1. Take last N prices (window_size = 5)
2. Calculate average of these prices
3. Compare current price to this average to determine trend

**Time Complexity:** O(K) where K = window size (constant = 5, so effectively O(1))

**Space Complexity:** O(K) for the slice

**Use case:** Smooths out price fluctuations to identify trends (UP/DOWN/STABLE)

**Could optimize with:** Deque for O(1) sliding window updates in streaming scenarios.

---

### Q9: How does your Top K algorithm work?

**Answer:**
I use Python's `heapq.nlargest()` which implements a **min heap** approach:

**Algorithm:**
1. Create a min heap of size K
2. Iterate through all N stocks
3. For each stock:
   - If heap size < K: add stock
   - If stock > smallest in heap: remove smallest, add new stock
4. Return heap contents (top K stocks)

**Time Complexity:** O(N log K)
- N iterations
- Each heap operation: O(log K)

**Space Complexity:** O(K) - only store K elements

**Why not full sort?**
- Full sort: O(N log N) time, O(N) space
- Heap: O(N log K) time, O(K) space
- When K << N, heap is significantly faster

**Example:** Top 5 from 1 million stocks:
- Sort: ~20 million operations
- Heap: ~5 million operations (4× faster!)

---

## 🔥 Advanced Questions

### Q10: What is the space-time tradeoff in your project?

**Answer:**
I made a deliberate **space-time tradeoff** in `storage.py`:

**Tradeoff:**
- **Extra Space:** Store each stock in 3 places:
  - `stocks_list` (for iteration)
  - `stocks_map` (for symbol lookup)
  - `sector_map` (for sector filtering)

**Benefit:**
- **Time Saved:**
  - Symbol lookup: O(N) → O(1)
  - Sector filtering: O(N) → O(1)

**Cost:**
- **Space:** 3× storage (references, not copies)
- **Maintenance:** Must update all 3 on add/delete

**Justification:** In stock market applications, **query speed is critical**. Users expect instant search results. The extra memory (just references) is negligible compared to the performance gain.

---

### Q11: How would you optimize your project for 1 million stocks?

**Answer:**
Current optimizations:
1. ✅ Hash table for O(1) lookups
2. ✅ Heap for Top K (O(N log K) vs O(N log N))
3. ✅ Sector map for filtered queries

**Further optimizations:**

1. **Database Integration:**
   - Use PostgreSQL with indexes
   - Offload storage from memory to disk
   - Enable distributed queries

2. **Caching Layer:**
   - Redis for frequently accessed stocks
   - Cache Top K results with TTL
   - Memoize expensive calculations

3. **Data Structures:**
   - **B-Tree** for range queries (price between $100-$500)
   - **Trie** for autocomplete in stock name search
   - **Bloom Filter** for existence checks before expensive lookups

4. **Algorithm Improvements:**
   - **Binary Search** on sorted price/volume data
   - **Parallel Processing** for sector analysis
   - **Lazy Evaluation** for large result sets

5. **Architecture:**
   - **Microservices** for different functionalities
   - **Load Balancing** for concurrent users
   - **Message Queue** for async updates

---

### Q12: Explain the difference between your project and Excel.

**Answer:**
**Key Differences:**

1. **Algorithm Implementation:**
   - **Excel:** Uses built-in functions (black box)
   - **My Project:** Implemented Quick Sort, Merge Sort, Heap algorithms from scratch

2. **Data Structures:**
   - **Excel:** 2D grid only
   - **My Project:** Hash tables, heaps, inverted indices, dynamic arrays

3. **Complexity Analysis:**
   - **Excel:** Hidden from user
   - **My Project:** Documented and optimized (O(1) lookups, O(N log K) Top K)

4. **Scalability:**
   - **Excel:** ~1M row limit, slows with formulas
   - **My Project:** Designed for growth with adaptive algorithms

5. **Automation:**
   - **Excel:** Manual operations
   - **My Project:** Background threads, API integration, real-time updates

6. **Learning Value:**
   - **Excel:** Tool usage
   - **My Project:** DSA understanding and implementation

**Bottom Line:** Excel is a tool. My project demonstrates **understanding of algorithms, data structures, and optimization techniques**.

---

## 💻 Implementation Questions

### Q13: Walk me through the code flow when a user searches for a stock.

**Answer:**
**User Input:** Search for "Apple"

**Flow:**

1. **CLI (`main.py` line 162-171):**
   ```python
   query = input("Enter search query: ")  # "Apple"
   results = self.search_manager.composite_search(query)
   ```

2. **Search Manager (`search.py` line 32-49):**
   ```python
   def composite_search(self, query: str):
       query_lower = query.lower()  # "apple"
       results = []
       seen_symbols = set()  # Prevent duplicates
       
       for stock in self.storage.get_all_stocks():
           if (query_lower in stock.symbol.lower() or 
               query_lower in stock.name.lower() or 
               query_lower in stock.sector.lower()):
               
               if stock.symbol not in seen_symbols:
                   results.append(stock)
                   seen_symbols.add(stock.symbol)
       
       return results
   ```

3. **Storage (`storage.py` line 63):**
   ```python
   def get_all_stocks(self):
       return self.stocks_list  # Returns list of all stocks
   ```

4. **Result Display:**
   - Prints all matching stocks
   - "AAPL - Apple Inc." would match

**Time Complexity:** O(N × L) where N = stocks, L = avg string length

**Optimization opportunity:** Could use Trie for O(L) prefix search.

---

### Q14: How does the live data update work?

**Answer:**
**Background Thread Implementation (`app.py` lines 39-63):**

```python
def background_refresh():
    while True:
        time.sleep(30)  # Wait 30 seconds
        
        # Fetch live data from yfinance API
        live_stocks = live_data_manager.fetch_top_stocks()
        
        # Update existing stocks
        for stock_data in live_stocks:
            existing_stock = storage.get_stock(stock_data['symbol'])
            if existing_stock:
                existing_stock.update_price(stock_data['price'])
        
        last_update_time = datetime.now()
        data_version += 1

# Start daemon thread
refresh_thread = threading.Thread(target=background_refresh, daemon=True)
refresh_thread.start()
```

**Flow:**
1. **Thread starts** when Flask app launches
2. **Every 30 seconds:**
   - Calls yfinance API
   - Gets current prices for top stocks
   - Updates prices in storage (O(1) hash lookup)
   - Increments version counter
3. **Frontend polls** `/api/last-update` to show timestamp
4. **Graphs auto-refresh** with new data

**Concurrency:** Daemon thread runs independently of main Flask thread.

---

### Q15: Explain your priority score calculation.

**Answer:**
**Formula (`ranking.py` line 23):**
```python
score = (stock.price * 0.5) + (stock.volume * 0.0001) - (stock.volatility * 50)
```

**Components:**

1. **Price (weight: 0.5):**
   - Higher price = higher score
   - Assumes established companies have higher prices

2. **Volume (weight: 0.0001):**
   - Higher trading volume = higher score
   - Indicates liquidity and investor interest
   - Small weight because volume is in millions

3. **Volatility (weight: -50, NEGATIVE):**
   - Higher volatility = lower score
   - Volatility represents risk
   - Penalty for unstable stocks

**Example:**
```
Stock: AAPL
Price: $150
Volume: 2,000,000
Volatility: 0.3

Score = (150 × 0.5) + (2,000,000 × 0.0001) - (0.3 × 50)
      = 75 + 200 - 15
      = 260
```

**Use Case:** Rank stocks by overall "quality" considering price, liquidity, and risk.

---

## 🎓 Conceptual Questions

### Q16: What is the difference between Quick Sort and Merge Sort?

**Answer:**

| Aspect | Quick Sort | Merge Sort |
|--------|-----------|------------|
| **Time (Average)** | O(N log N) | O(N log N) |
| **Time (Worst)** | O(N²) | O(N log N) |
| **Space** | O(log N) | O(N) |
| **Stability** | Unstable | Stable |
| **Method** | Divide & Conquer (in-place) | Divide & Conquer (external) |
| **Best for** | Small/medium data, random | Large data, guaranteed performance |

**Quick Sort:**
- Picks a pivot, partitions around it
- Faster in practice due to cache locality
- Risk of O(N²) with bad pivot selection

**Merge Sort:**
- Divides in half, recursively sorts, merges
- Predictable performance
- Requires extra memory for merging

**My Implementation:** Uses Quick Sort for small datasets (< 10 stocks) for speed, Merge Sort for large datasets for reliability.

---

### Q17: What is a hash collision and how is it handled?

**Answer:**
**Hash Collision:** When two different keys produce the same hash value.

**Example:**
```python
hash("AAPL") = 12345
hash("MSFT") = 12345  # Collision!
```

**Python Dictionary Handling:**
1. **Open Addressing:** Probes for next available slot
2. **Chaining:** Stores colliding items in a linked list at that index

**In my project:**
- Python's `dict` handles collisions automatically
- Uses open addressing with quadratic probing
- Average case still O(1) due to dynamic resizing

**Load Factor:** Python resizes when dictionary is ~2/3 full to maintain O(1) performance.

**Why it doesn't affect my project:** Stock symbols are unique strings, well-distributed hash values, low collision probability.

---

### Q18: Explain Big O notation with examples from your project.

**Answer:**
**Big O** describes how algorithm performance scales with input size.

**Examples from my project:**

1. **O(1) - Constant Time:**
   ```python
   stock = self.stocks_map.get(symbol)  # Hash table lookup
   ```
   - Same time regardless of 10 or 10,000 stocks

2. **O(N) - Linear Time:**
   ```python
   for stock in self.storage.get_all_stocks():  # Iterate all stocks
   ```
   - Time doubles when stocks double

3. **O(log N) - Logarithmic Time:**
   ```python
   # Binary search on sorted prices (if implemented)
   ```
   - Time increases slowly (1000 stocks = 10 ops, 1M stocks = 20 ops)

4. **O(N log N) - Linearithmic Time:**
   ```python
   self._merge_sort(stocks, key_func)  # Merge Sort
   ```
   - Optimal for comparison-based sorting

5. **O(N log K) - Heap Selection:**
   ```python
   heapq.nlargest(k, all_stocks, key=...)  # Top K
   ```
   - Better than O(N log N) when K << N

**Why it matters:** Helps choose the right algorithm for performance requirements.

---

### Q19: What is the difference between space complexity and time complexity?

**Answer:**

**Time Complexity:** How execution time grows with input size
**Space Complexity:** How memory usage grows with input size

**Examples from my project:**

**Merge Sort:**
- **Time:** O(N log N) - must compare and merge all elements
- **Space:** O(N) - needs temporary array for merging

**Quick Sort:**
- **Time:** O(N log N) average - partitions in-place
- **Space:** O(log N) - recursion stack depth

**Hash Table Lookup:**
- **Time:** O(1) - direct access
- **Space:** O(N) - must store all elements

**Top K Heap:**
- **Time:** O(N log K) - process all N, maintain K
- **Space:** O(K) - only store K elements

**Tradeoff in my project:**
- Used 3× storage (space) for O(1) lookups (time)
- Acceptable because memory is cheap, speed is critical

---

### Q20: Why did you choose Python for this project?

**Answer:**

**Advantages:**
1. **Built-in Data Structures:**
   - `dict` (hash table), `list` (dynamic array), `set`
   - `heapq` module for heap operations
   - Focus on algorithm logic, not implementation details

2. **Readability:**
   - Clean syntax for demonstrating DSA concepts
   - Easy for teachers to review

3. **Libraries:**
   - `yfinance` for live stock data
   - `Flask` for web dashboard
   - `threading` for background updates

4. **Rapid Development:**
   - Quick prototyping and iteration
   - Good for academic projects

**Disadvantages:**
- Slower than C/C++ (interpreted vs compiled)
- GIL (Global Interpreter Lock) limits true parallelism

**For DSA learning:** Python is excellent because it lets you focus on **algorithm design** rather than memory management.

---

## 🚀 Project-Specific Questions

### Q21: How many stocks can your system handle?

**Answer:**
**Current Capacity:**
- **In-memory:** Limited by RAM (~100K-1M stocks)
- **Performance:** Optimized for 1K-100K stocks

**Bottlenecks:**
1. **Memory:** All stocks stored in RAM
2. **Search:** O(N) for composite search
3. **Updates:** O(N) for market sentiment calculation

**Tested with:** 15 stocks (demo), designed for 10K+

**Scalability improvements:**
1. Database integration (PostgreSQL)
2. Pagination for large result sets
3. Caching frequently accessed data
4. Indexing for faster searches

**Real-world comparison:**
- NYSE has ~2,800 stocks
- NASDAQ has ~3,300 stocks
- My system can handle this comfortably

---

### Q22: What happens if two users update the same stock simultaneously?

**Answer:**
**Current Implementation:** Not thread-safe for writes

**Problem:**
```python
# User 1: Updates AAPL price to $150
# User 2: Updates AAPL price to $151 (simultaneously)
# Result: Race condition - last write wins
```

**Solutions:**

1. **Locking (Mutex):**
   ```python
   import threading
   lock = threading.Lock()
   
   with lock:
       stock.update_price(new_price)
   ```

2. **Database Transactions:**
   - ACID properties ensure consistency
   - Isolation levels prevent conflicts

3. **Message Queue:**
   - Serialize updates through queue
   - Process sequentially

4. **Optimistic Locking:**
   - Version numbers on each stock
   - Reject update if version changed

**For this project:** Single-user CLI or low-traffic web app, so race conditions are unlikely. In production, would use database transactions.

---

### Q23: How do you handle invalid input?

**Answer:**
**Current Validation:**

1. **Type Checking:**
   ```python
   try:
       price = float(input("Price: "))
       volume = int(input("Volume: "))
   except ValueError:
       print("Invalid input!")
   ```

2. **Range Validation:**
   ```python
   volatility = float(input("Volatility (0-1): "))
   if not 0 <= volatility <= 1:
       print("Volatility must be between 0 and 1")
   ```

3. **Existence Checks:**
   ```python
   stock = storage.get_stock(symbol)
   if not stock:
       print("Stock not found!")
       return
   ```

**Could improve with:**
- Input sanitization (prevent SQL injection if using DB)
- Regex validation for stock symbols (e.g., 1-5 uppercase letters)
- Bounds checking for price/volume (must be positive)
- Exception handling for API failures

---

### Q24: Explain the sector map data structure.

**Answer:**
**Structure (`storage.py` line 14):**
```python
self.sector_map: Dict[str, List[Stock]] = {}

# Example:
{
    "Tech": [AAPL, GOOGL, MSFT, NVDA],
    "Finance": [JPM, V],
    "Health": [JNJ, PFE]
}
```

**Purpose:** **Inverted Index** for fast sector-based queries

**Operations:**

1. **Add Stock:**
   ```python
   if stock.sector not in self.sector_map:
       self.sector_map[stock.sector] = []
   self.sector_map[stock.sector].append(stock)
   ```
   - Time: O(1) hash lookup + O(1) list append

2. **Get Stocks by Sector:**
   ```python
   return self.sector_map.get(sector, [])
   ```
   - Time: O(1) hash lookup
   - Returns list of stocks in that sector

**Without sector map:**
```python
# Would need O(N) linear scan
results = [s for s in stocks if s.sector == "Tech"]
```

**With sector map:**
```python
# O(1) lookup
results = sector_map["Tech"]
```

**Tradeoff:** Extra memory for O(1) sector filtering.

---

### Q25: What testing did you perform?

**Answer:**
**Testing Performed:**

1. **Functional Testing:**
   - Tested all 9 menu options in CLI
   - Verified add/update/search/sort/rank operations
   - Checked edge cases (empty results, invalid input)

2. **Data Validation:**
   - Live data fetching from yfinance
   - Fallback to dummy data if API fails
   - Price history generation

3. **Algorithm Verification:**
   - Quick Sort vs Merge Sort with different dataset sizes
   - Top K results match manual calculation
   - Moving average calculation accuracy

4. **Performance Testing:**
   - Timed operations with varying stock counts
   - Verified O(1) hash lookups
   - Compared heap vs sort for Top K

**Could improve with:**
- Unit tests (pytest) for each function
- Integration tests for API endpoints
- Load testing for concurrent users
- Edge case testing (empty data, large datasets)

---

## 🎯 Closing Questions

### Q26: What did you learn from this project?

**Answer:**
**Technical Skills:**
1. **Data Structure Selection:** Learned when to use hash tables vs lists vs heaps
2. **Algorithm Analysis:** Understanding time/space complexity tradeoffs
3. **Optimization:** Hybrid algorithms, caching, indexing
4. **Real-world Application:** Applying DSA to practical problems

**Soft Skills:**
1. **Problem Decomposition:** Breaking complex problems into smaller parts
2. **Design Decisions:** Justifying choices with complexity analysis
3. **Documentation:** Writing clear, maintainable code

**Key Takeaway:** **The right data structure can transform O(N) to O(1).** Small design decisions have huge performance impacts at scale.

---

### Q27: What would you improve if you had more time?

**Answer:**
**Improvements:**

1. **Advanced Data Structures:**
   - **Trie** for autocomplete in stock search
   - **B-Tree** for range queries (stocks between $100-$500)
   - **Graph** for sector correlation analysis

2. **Algorithms:**
   - **Binary Search** on sorted data
   - **Dynamic Programming** for portfolio optimization
   - **Graph Algorithms** (BFS/DFS) for sector relationships

3. **Features:**
   - Historical data analysis with time-series algorithms
   - Predictive analytics using machine learning
   - Real-time WebSocket updates instead of polling

4. **Architecture:**
   - Database integration (PostgreSQL with indexes)
   - Redis caching layer
   - Microservices architecture
   - API rate limiting and authentication

5. **Testing:**
   - Comprehensive unit tests
   - Performance benchmarks
   - Load testing for scalability

---

### Q28: How is this project relevant to industry?

**Answer:**
**Real-World Applications:**

1. **Financial Services:**
   - Trading platforms use similar data structures
   - High-frequency trading requires O(1) lookups
   - Risk analysis uses statistical algorithms

2. **E-commerce:**
   - Product search uses inverted indices
   - Top K recommendations use heap algorithms
   - Sorting by price/rating uses hybrid sorts

3. **Social Media:**
   - News feed ranking uses priority scores
   - Trending topics use frequency analysis
   - User search uses hash tables

**Skills Demonstrated:**
- Algorithm optimization for performance
- Data structure selection for use case
- API integration and background processing
- Web development with real-time updates

**Industry Relevance:** Shows I can **apply DSA concepts to solve real problems efficiently**, not just implement textbook examples.

---

### Q29: Defend your project against the "Excel can do this" argument.

**Answer:**
**My Response:**

"While Excel can perform similar calculations, my project fundamentally differs in **purpose and demonstration**:

**1. Implementation vs Usage:**
- Excel: Uses `=SORT()` - black box
- My Project: Implemented Quick Sort and Merge Sort from scratch

**2. Data Structure Design:**
- Excel: 2D grid only
- My Project: Hash tables, heaps, inverted indices - each chosen for specific performance characteristics

**3. Complexity Analysis:**
- Excel: Hidden from user
- My Project: Every function documented with Big O notation

**4. Optimization:**
- Excel: Automatic
- My Project: Deliberate design decisions (heap for Top K, hybrid sorting, redundant storage for speed)

**5. Learning Objective:**
- Excel: Tool usage
- My Project: DSA understanding, algorithm implementation, performance optimization

**The goal isn't just to analyze stocks - it's to demonstrate mastery of data structures and algorithms through a practical application. Excel is a tool. My project is a learning demonstration.**"

---

### Q30: Any final thoughts on your project?

**Answer:**
"This project taught me that **DSA isn't just academic theory** - it's about making smart engineering decisions:

- Choosing hash tables for O(1) lookups saved massive time
- Using heaps for Top K instead of full sorting showed optimization thinking  
- Implementing hybrid sorting demonstrated understanding of algorithm tradeoffs
- Building a real application proved I can apply DSA to solve practical problems

**Most importantly:** I learned that **the right data structure can be the difference between a slow, unusable application and a fast, scalable system.**

I'm proud of this project because it shows I don't just know DSA concepts - I know **when and why to use them**."

---

## 📊 Quick Reference Tables

### Time Complexity Summary

| Operation | Complexity | Data Structure |
|-----------|-----------|----------------|
| Add Stock | O(1) | Hash Table |
| Get Stock by Symbol | O(1) | Hash Table |
| Search by Name | O(N) | Linear Scan |
| Get Stocks by Sector | O(1) | Sector Map |
| Top K Stocks | O(N log K) | Heap |
| Sort All Stocks | O(N log N) | Hybrid Sort |
| Moving Average | O(K) ≈ O(1) | Sliding Window |
| Market Sentiment | O(N × K) | Iteration |

### Data Structure Comparison

| Structure | Used For | Time | Space |
|-----------|----------|------|-------|
| Hash Table | Symbol lookup | O(1) | O(N) |
| List | All stocks | O(N) search | O(N) |
| Sector Map | Sector filter | O(1) | O(N) |
| Heap | Top K | O(N log K) | O(K) |
| Set | Deduplication | O(1) | O(N) |

---

## 🎓 Tips for Viva

1. **Be Confident:** You built this, you understand it
2. **Use Examples:** "For instance, with 10,000 stocks..."
3. **Draw Diagrams:** Sketch data structures if needed
4. **Admit Limitations:** "This could be improved with..."
5. **Show Enthusiasm:** Talk about what you learned
6. **Know Your Code:** Be ready to explain any line
7. **Complexity First:** Always mention Big O when discussing algorithms
8. **Real-World Context:** Relate to industry applications

---

**Good luck with your viva! 🚀**
