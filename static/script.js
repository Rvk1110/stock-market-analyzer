const API_BASE = '/api';

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    const pageId = document.body.getAttribute('data-page');

    if (pageId === 'market') {
        fetchSentiment();
        fetchTopK();
        fetchSectors();
    } else if (pageId === 'stocks') {
        fetchStocks();
    } else if (pageId === 'sectors') {
        fetchSectorDetails();
    }
});

// Fetch All Stocks
async function fetchStocks(sort = 'price', order = 'asc') {
    const res = await fetch(`${API_BASE}/stocks?sort=${sort}&order=${order}`);
    const stocks = await res.json();
    renderTable(stocks);
}

function renderTable(stocks) {
    const tbody = document.getElementById('stockTableBody');
    tbody.innerHTML = '';

    stocks.forEach(s => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-weight: bold; color: var(--accent)">${s.symbol}</td>
            <td>${s.name}</td>
            <td><span style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px; font-size: 0.8em">${s.sector}</span></td>
            <td>$${s.price.toFixed(2)}</td>
            <td>${s.volume.toLocaleString()}</td>
            <td>${s.volatility}</td>
            <td>
                <button onclick="viewTrend('${s.symbol}')" style="font-size: 0.8em; padding: 4px 8px">Stats</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Search
let searchTimeout;
function handleSearch(e) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
        const query = e.target.value;
        if (!query) {
            fetchStocks();
            return;
        }

        const res = await fetch(`${API_BASE}/search?q=${query}`);
        const results = await res.json();
        renderTable(results);
    }, 300);
}

// Rankings
async function fetchTopK() {
    const type = document.getElementById('rankingCriteria').value;
    const res = await fetch(`${API_BASE}/top-k?k=5&type=${type}`);
    const data = await res.json();

    const list = document.getElementById('topKList');
    list.innerHTML = '';

    data.forEach((s, i) => {
        const li = document.createElement('li');
        let extra = '';
        if (type === 'score' && s.score) extra = `<span class="rank-score">Score: ${s.score.toFixed(2)}</span>`;
        else if (type === 'volume') extra = `<span class="rank-score">${s.volume.toLocaleString()} vol</span>`;
        else extra = `<span class="rank-score">$${s.price.toFixed(2)}</span>`;

        li.innerHTML = `
            <div style="display: flex; gap: 10px; align-items: center">
                <span style="font-weight: bold; color: var(--text-secondary)">#${i + 1}</span>
                <span>${s.name} (${s.symbol})</span>
            </div>
            ${extra}
        `;
        list.appendChild(li);
    });
}

// Sentiment
async function fetchSentiment() {
    const res = await fetch(`${API_BASE}/sentiment`);
    const data = await res.json();

    const container = document.getElementById('sentimentContainer');
    container.innerHTML = `
        <div><span>Running Bull (UP)</span> <span class="trend-up">${data.UP || 0}</span></div>
        <div><span>Bearish (DOWN)</span> <span class="trend-down">${data.DOWN || 0}</span></div>
        <div><span>Sideways (STABLE)</span> <span class="trend-stable">${data.STABLE || 0}</span></div>
    `;
}

// Sector Performance (Summary for Dashboard)
async function fetchSectors() {
    const res = await fetch(`${API_BASE}/sectors`);
    const data = await res.json();

    const tbody = document.getElementById('sectorTableBody');
    if (tbody) {
        tbody.innerHTML = '';
        data.forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${s.sector} <span style="font-size:0.8em; color:var(--text-secondary)">(${s.count})</span></td>
                <td>$${s.avg_price.toFixed(2)}</td>
                <td>${s.total_volume.toLocaleString()}</td>
            `;
            tbody.appendChild(tr);
        });
    }
}

// Full Sector Details (Chart + Deep Table)
async function fetchSectorDetails() {
    const res = await fetch(`${API_BASE}/sectors`);
    const data = await res.json();

    // Render Table
    const tbody = document.getElementById('sectorFullTableBody');
    tbody.innerHTML = '';
    data.forEach(s => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span style="font-weight:bold; color:var(--accent)">${s.sector}</span></td>
            <td>${s.count}</td>
            <td>$${s.avg_price.toFixed(2)}</td>
            <td>${s.total_volume.toLocaleString()}</td>
            <td>${s.avg_volatility.toFixed(3)}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Add Stock
function toggleModal() {
    const modal = document.getElementById('modal');
    modal.style.display = modal.style.display === 'block' ? 'none' : 'block';
}

async function handleAddStock(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    await fetch(`${API_BASE}/stocks`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    toggleModal();
    e.target.reset();
    fetchStocks();
    fetchSentiment(); // Updates might change sentiment
}

// View Trend (Simple Alert for Demo)
async function viewTrend(symbol) {
    const res = await fetch(`${API_BASE}/trend/${symbol}`);
    const data = await res.json();
    alert(`Trend Analysis for ${data.symbol}:\nDirectory: ${data.trend}\nSMA (Window 5): ${data.sma.toFixed(2)}\nHistory: ${data.history}`);
}
