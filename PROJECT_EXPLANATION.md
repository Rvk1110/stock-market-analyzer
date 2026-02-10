# Stock Market Analyzer - Comprehensive Project Technical Documentation

## 1. Project Architecture & Design Philosophy
This project is a sophisticated **Web-Based Stock Market Simulation Engine** built to demonstrate high-performance data processing and visualization. It follows a modular **Model-View-Controller (MVC)** architectural pattern, adapted for a modern Flask web application.

### A. Backend Core (Python/Flask)
The backend is not just a simple API; it serves as a **stateful simulation engine**. Unlike typical stateless web apps, this application maintains a live memory state of the stock market to simulate real-time changes.
-   **`app.py`**: The central controller. It initializes the Flask application and orchestrates the interaction between the data storage, analysis modules, and the frontend. It uses **multithreading** (`threading.Thread`) to run a background process (`background_refresh`) that continuously updates stock prices, simulating a live market feed without blocking user requests.
-   **`models.py`**: Defines the data structure. The `Stock` class is a data class that enforces strict typing for stock attributes (Symbol, Price, Volume), ensuring data integrity throughout the system.
-   **`storage.py`**: Acts as an in-memory database. It uses **Hash Maps (Python Dictionaries)** for $O(1)$ access time, ensuring that fetching any specific stock is an instant operation, even if the dataset grows to millions of entries.

### B. Frontend Architecture (HTML/CSS/JS)
The frontend is designed for **high responsiveness and interactivity**.
-   **Template Inheritance**: Uses Jinja2 templating (`base.html`) to maintain a consistent layout and reduce code duplication.
-   **Dynamic Updates**: JavaScript (via `fetch` API) is used to asynchronously load data. This means the page doesn't need to reload to show new prices or search results, providing a "Single Page Application" (SPA) feel.

---

## 2. Deep Dive: Charts and Visualization Technology
The project uses **Chart.js**, an industry-standard JavaScript library, to render complex data visualizations. This is not just "plug-and-play"; specific configurations were chosen to enhance data readability.

### Price History Chart (`stock_detail.html`)
This is a **Dual-Dataset Line Chart** that combines raw data with analytical overlays.
1.  **The Price Dataset (Visualizing Volatility)**:
    -   **Gradient Fill**: The area under the line uses a linear gradient (fading from opaque blue to transparent). This is a UX choice to make the "volume" of the price feel substantial and to visually anchor the line to the x-axis.
    -   **Tension**: A tension of `0.4` is applied to the Bezier curves. This smooths the line connecting data points, making the chart easier to read than a jagged raw-data line.

2.  **The SMA Overlay (Visualizing Trends)**:
    -   **Dashed Line Style**: The Simple Moving Average is rendered as a dashed line (`borderDash: [5, 5]`) to visually distinguish it from the actual price.
    -   **Context**: By overlaying this on the price chart, users can instantly see if the current price is "overextended" (far above the average) or "oversold" (far below the average).

3.  **Technical Implementation**:
    -   The chart uses an HTML5 `<canvas>` element.
    -   Data is passed dynamically from the Python backend -> Jinja2 Template -> JavaScript variable -> Chart.js configuration.
    -   **Responsiveness**: The `maintainAspectRatio: false` option is used so the chart automatically resizes to fit tablet or mobile screens perfectly.

---

## 3. Data Structures and Algorithms (DSA) - Technical Analysis
The core value of this project lies in its efficient use of algorithms to handle data. Below is a detailed breakdown of every algorithm used, *why* it was chosen, and its performance characteristics.

### A. Hybrid Sorting Engine (`sorting.py`)
Sorting is critical for features like "Top Gainers" or sorting by Volume. We implement a **Hybrid Sort** that combines the best of two worlds.

1.  **Quick Sort (The Speedster)**:
    -   **Logic**: It picks a "pivot" element and partitions the array into three parts: elements smaller than pivot, equal to pivot, and larger than pivot. It then recursively sorts the sub-arrays.
    -   **Why use it?**: For small arrays, Quick Sort has very low constant factors and memory overhead, making it faster than Merge Sort in practice.
    -   **Complexity**: Average $O(N \log N)$, Worst Case $O(N^2)$.
    -   **Implementation**: We use this when `len(stocks) < threshold` (default 50).

2.  **Merge Sort (The Reliable Workhorse)**:
    -   **Logic**: It recursively divides the array in half until individual elements remain, then "merges" them back together in sorted order.
    -   **Why use it?**: Merge Sort is **Stable** (preserves order of equal elements) and has a **guaranteed** worst-case time of $O(N \log N)$. It never degrades to $O(N^2)$ like Quick Sort can.
    -   **Implementation**: We switch to this automatically for larger datasets to ensure system stability.

### B. Intelligent Searching (`search.py`)
Search is not just scanning a list; it's about relevance and speed.

1.  **Composite Search Logic**:
    -   **Problem**: Users might query "Tech", "Apple", or "AAPL". A simple check isn't enough.
    -   **Solution**: The `composite_search` function performs a multi-field verification. It checks `if query in symbol OR query in name OR query in sector`.
    -   **Optimization (The Set Data Structure)**:
        -   When combining results from different matching criteria, you risk duplicates.
        -   We use a **HashSet** (`seen_symbols = set()`) to track added stocks.
        -   **Benefit**: Checking if an item exists in a Set is **$O(1)$** (instant), whereas checking a List is $O(N)$. This makes the deduplication process incredibly fast.

### C. Advanced Ranking with Heaps (`ranking.py`)
When you see "Top 5 Stocks" on the dashboard, we do NOT sort the whole list. Sorting 10,000 stocks just to get the top 5 is wasteful.

1.  **Min-Heaps and Max-Heaps**:
    -   **Algorithm**: We use the `heapq` algorithm (part of Python's standard library). A Heap is a specialized tree-based data structure that satisfies the heap property (parent is always greater/smaller than children).
    -   **Logic**: To get the Top $K$ items, we build a heap of the dataset and pop $K$ times.
    -   **Performance Optimization**:
        -   Full Sort: $O(N \log N)$
        -   Heap Approach: **$O(N + K \log N)$** (building heap is $O(N)$).
        -   **Impact**: For a large dataset (e.g., 1 million stocks) where we only need the top 10, the Heap approach is orders of magnitude faster than sorting.

2.  **Custom Scoring Algorithm**:
    -   We don't just rank by price. We calculate a `Priority Score`:
    -   `Score = (Price * 0.5) + (Volume * 0.0001) - (Volatility * 50)`
    -   This formula rewards high-value, high-liquidity stocks while penalizing high-risk (volatile) ones, giving a "Quality" metric for ranking.

### D. Trend Analysis via Sliding Windows (`trend_analysis.py`)
To determine if a stock is "Bullish" or "Bearish", we analyze its history using a **Sliding Window**.

1.  **The Sliding Window Technique**:
    -   **Concept**: Instead of analyzing the entire history of a stock (which could be years of data), we look at a fixed "window" of the most recent $N$ days (e.g., 5 days).
    -   **Implementation**: We use `collections.deque` (Double-Ended Queue).
    -   **Why Deque?**: A deque allows adding and removing elements from both ends in **$O(1)$** time. A standard list requires $O(N)$ to remove the first element (shifting all others).
    -   **The Algorithm**:
        1.  Extract the last $N$ prices (The Window).
        2.  Calculate the Average (SMA).
        3.  Compare current price to SMA.
        4.  If `Price > SMA + threshold` -> **UP Trend**.

---

## 4. Summary of DSA Efficiency
| Feature | Algorithm/DS Used | Complexity | Benefit |
| :--- | :--- | :--- | :--- |
| **Stock Storage** | Hash Map (Dict) | $O(1)$ | Instant access by Symbol |
| **Search** | Set (HashSet) | $O(1)$ | Fast deduplication of results |
| **Top 5 Lists** | Heap (Priority Queue) | $O(N + K \log N)$ | Faster than sorting for top-k items |
| **Sorting** | Hybrid (Merge/Quick) | $O(N \log N)$ | Stability and Speed balance |
| **Trend Calc** | Sliding Window (Deque) | $O(K)$ | Efficient time-series analysis |

---

## 5. Portfolio Analysis - DSA Based Implementation
The **Portfolio Analysis** module is a deterministic, algorithm-driven system that evaluates a user's personal holdings without any AI or Machine Learning. It relies strictly on mathematical models and efficient data structures.

### A. Core Data Structures
1.  **Hash Map (Dictionary)** for Storage:
    -   **Usage**: Stores portfolio holdings keyed by stock symbol.
    -   **Why**: Provides $O(1)$ access for updates (buying more shares) and lookups.
2.  **Set** for Diversity Tracking:
    -   **Usage**: Maintains a collection of unique investment platforms (e.g., Zerodha, Groww).
    -   **Why**: Allows for $O(1)$ insertion and distinct counting to calculate the Diversification Score.
3.  **Heaps** for Ranking:
    -   **Usage**: Used to identify "Top 3 Profitable Stocks" and "Highest Risk Holdings".
    -   **Why**: Extracting the top $K$ elements from $N$ holdings is $O(N \log K)$, which is optimal for dynamic dashboards.

### B. Algorithmic Portfolio Score
The **Portfolio Health Score** (0-100) is calculated using a transparent, weighted formula:
$$ Score = (ProfitScore \times 0.4) + (DiversityScore \times 0.2) + (RiskScore \times 0.4) $$
-   **Profit Score**: Linear mapping of Profit% (capped at +/- 20%).
-   **Diversity Score**: Based on the count of unique platforms (encouraging broker diversification).
-   **Risk Score**: Inverse function of the portfolio's average volatility (lower volatility = higher score).
