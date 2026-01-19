# 📈 Stock Market Analyzer: Comprehensive Project Manual

This document provides both a simple overview for laymen and a detailed technical breakdown of the project's inner workings.

---

## Part 1: Simple Explanation (Laymen Terms)

Welcome to the **Stock Market Analyzer**! This project is a powerful tool designed to help you track, analyze, and understand the stock market using some of the coolest techniques in computer science.

### 1. What is this project?
Think of this project as a **Personal Financial Assistant**. It pulls real-time data from the actual stock market (like Apple, Google, and Tesla) and organizes it so you can see:
*   **Performance**: Which stocks are making money right now.
*   **Industry Trends**: Which sectors (like Tech, Healthcare, or Energy) are the most active.
*   **Price History**: How prices have changed over time.

### 2. How does it get the data?
Instead of manually typing in prices, the project uses a "bridge" called an **API** (Application Programming Interface).
*   **The Source**: We use a service called `yfinance` (Yahoo Finance).
*   **The Process**: Every 30 seconds, our code "calls" Yahoo Finance and says, *"Hey, what's the latest price for Apple?"*
*   **The Result**: The information is instantly updated on your dashboard without you having to refresh the page.

### 3. The "Brain" of the Project (Simplified DSA)
In programming, we use **Data Structures and Algorithms (DSA)** to make things fast and organized.
*   **Hash Tables**: Used for instant lookups (like an index in a book).
*   **Heaps**: Used for leaderboards (Top 5 stocks).
*   **Hybrid Sorting**: A mix of two fast methods to keep the tables organized instantly.

---

## Part 2: Detailed Technical Manual (Deep Dive)

### 🏗️ Project Architecture
The system is built as a **Modular Python Application** that combines a high-performance backend with a dynamic web frontend.

#### File-by-File Breakdown:
*   **`models.py`**: Defines the blueprint for every stock (price, volume, volatility).
*   **`storage.py`**: The in-memory database using **Hash Tables** for O(1) retrieval speed.
*   **`sorting.py`**: Implements a **Hybrid Sort** (Quick Sort + Merge Sort) for efficient data organization.
*   **`ranking.py`**: Uses **Heaps** to find Top-K stocks with minimal processing power.
*   **`search.py`**: A composite search engine for symbols and names.
*   **`live_data.py`**: The API integration layer with `yfinance`.
*   **`app.py`**: The Flask server that manages the background threading and API endpoints.

### 📡 Data Flow & Procedure

#### 1. Initialization
When `app.py` is executed:
1.  The storage is cleared and initialized.
2.  An initial fetch pulls live data for 20+ tracked symbols.
3.  The Flask server begins listening on port `5001`.

#### 2. Background Synchronization
A **background thread** is spawned. This thread runs independently of the web dashboard, fetching fresh data every 30 seconds to ensure the mathematical models (averages, sentiment) are always accurate.

#### 3. Request Lifecycle
When a user clicks a tab on the dashboard:
1.  **Frontend**: The browser sends a GET request to `/api/stocks` or `/api/top-k`.
2.  **Backend**: Flask intercepts this, calls the relevant DSA module (e.g., `RankingManager`), processes the data, and returns it as **JSON**.
3.  **Visualization**: The browser uses **`Chart.js`** to turn that raw data into interactive graphs.

### ⚙️ Performance Highlights
*   **Low Overhead**: By using Heaps for ranking, we avoid sorting the entire dataset multiple times, which keeps CPU usage low.
*   **Thread Safety**: The background refresh is designed to update the price history without interrupting the user's view.
*   **Modular Design**: Every component (Search, Sort, Rank) is independent, making it easy to upgrade or swap parts.

---

### Final Summary
This project represents a complete end-to-end data pipeline: from raw financial APIs to complex algorithmic processing, ending with a beautiful and intuitive user interface.
