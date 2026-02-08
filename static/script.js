const API_BASE = '/api';

// Real-time update variables
let updateInterval = null;
let isUpdating = true;
let lastDataVersion = 0;

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    const pageId = document.body.getAttribute('data-page');

    if (pageId === 'market') {
        fetchSentiment();
        fetchTopK();
        fetchSectors();
        fetchTopCharts();
        fetchRiskAnalysis();

        // Start real-time updates
        startRealTimeUpdates();
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
        tr.style.cursor = 'pointer';
        tr.onclick = () => window.location.href = `/stock/${s.symbol}`;

        tr.innerHTML = `
            <td style="font-weight: bold; color: var(--accent)">${s.symbol}</td>
            <td>${s.name}</td>
            <td><span style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px; font-size: 0.8em">${s.sector}</span></td>
            <td>$${s.price.toFixed(2)}</td>
            <td>${s.volume.toLocaleString()}</td>
            <td>${s.volatility}</td>
            <td>
                <button onclick="event.stopPropagation(); viewTrend('${s.symbol}')" style="font-size: 0.8em; padding: 4px 8px">Stats</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Search
// Search
let searchTimeout;
function handleSearch(e) {
    clearTimeout(searchTimeout);

    // Show loading state immediately if query exists
    const query = e.target.value;
    const tbody = document.getElementById('stockTableBody');

    if (!query) {
        fetchStocks();
        return;
    }

    // Show searching feedback
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 20px; color: var(--text-secondary);">🔍 Searching market data... (this may take a moment)</td></tr>';

    searchTimeout = setTimeout(async () => {
        try {
            const res = await fetch(`${API_BASE}/search?q=${query}`);
            const results = await res.json();

            if (results.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 20px; color: var(--text-secondary);">No results found for "${query}" locally or in live market.</td></tr>`;
            } else {
                renderTable(results);
            }
        } catch (error) {
            console.error("Search error:", error);
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color: var(--danger);">Error performing search.</td></tr>';
        }
    }, 600); // Increased debounce to 600ms to allow typing to finish
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
// Sentiment Chart
// Sentiment
// Sentiment Chart
async function fetchSentiment() {
    const res = await fetch(`${API_BASE}/sentiment`);
    const data = await res.json();

    const ctx = document.getElementById('sentimentChart');
    if (ctx) {
        if (window.sentimentChartInstance) window.sentimentChartInstance.destroy();

        window.sentimentChartInstance = new Chart(ctx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Up', 'Down', 'Stable'],
                datasets: [{
                    data: [data.UP || 0, data.DOWN || 0, data.STABLE || 0],
                    backgroundColor: ['#10b981', '#ef4444', '#94a3b8'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#e2e8f0',
                            font: { family: 'Inter', size: 11 },
                            usePointStyle: true,
                            boxWidth: 8
                        }
                    }
                }
            }
        });
    }
}

// Sector Performance Charts (Price Bar + Volume Pie)
async function fetchSectors() {
    const res = await fetch(`${API_BASE}/sectors`);
    const data = await res.json();

    // 1. Sector Price Bar Chart
    const priceCtx = document.getElementById('sectorPriceChart');
    if (priceCtx) {
        if (window.sectorPriceChartInstance) window.sectorPriceChartInstance.destroy();

        const labels = data.map(s => s.sector);
        const prices = data.map(s => s.avg_price);

        const ctx = priceCtx.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(99, 102, 241, 0.8)');
        gradient.addColorStop(1, 'rgba(99, 102, 241, 0.2)');

        window.sectorPriceChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Avg Price ($)',
                    data: prices,
                    backgroundColor: gradient,
                    borderColor: '#6366f1',
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', font: { family: 'Inter', size: 10 } }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // 2. Sector Volume Chart
    const volumeCtx = document.getElementById('sectorVolumeChart');
    if (volumeCtx) {
        if (window.sectorVolumeChartInstance) window.sectorVolumeChartInstance.destroy();

        const labels = data.map(s => s.sector);
        const volumes = data.map(s => s.total_volume);

        window.sectorVolumeChartInstance = new Chart(volumeCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: volumes,
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(139, 92, 246, 0.8)'
                    ],
                    borderColor: 'rgba(255, 255, 255, 0.05)',
                    borderWidth: 2,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#94a3b8',
                            font: { family: 'Inter', size: 11 },
                            boxWidth: 12,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
}

// Top 5 Charts (Price and Volume)
async function fetchTopCharts() {
    // Top 5 by Price
    const priceRes = await fetch(`${API_BASE}/top-k?k=5&type=price`);
    const priceData = await priceRes.json();

    const priceCtx = document.getElementById('topPriceChart');
    if (priceCtx) {
        const ctx = priceCtx.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 400, 0);
        gradient.addColorStop(0, 'rgba(16, 185, 129, 0.8)');
        gradient.addColorStop(1, 'rgba(16, 185, 129, 0.2)');

        if (window.topPriceChartInstance) window.topPriceChartInstance.destroy();

        window.topPriceChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: priceData.map(s => s.symbol),
                datasets: [{
                    label: 'Price ($)',
                    data: priceData.map(s => s.price),
                    backgroundColor: gradient,
                    borderColor: '#10b981',
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#f0f2f5', font: { family: 'Inter', weight: '600' } },
                        border: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // Top 5 by Volume
    const volumeRes = await fetch(`${API_BASE}/top-k?k=5&type=volume`);
    const volumeData = await volumeRes.json();

    const volumeCtx = document.getElementById('topVolumeChart');
    if (volumeCtx) {
        const ctx = volumeCtx.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 400, 0);
        gradient.addColorStop(0, 'rgba(245, 158, 11, 0.8)');
        gradient.addColorStop(1, 'rgba(245, 158, 11, 0.2)');

        if (window.topVolumeChartInstance) window.topVolumeChartInstance.destroy();

        window.topVolumeChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: volumeData.map(s => s.symbol),
                datasets: [{
                    label: 'Volume',
                    data: volumeData.map(s => s.volume),
                    backgroundColor: gradient,
                    borderColor: '#f59e0b',
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#f0f2f5', font: { family: 'Inter', weight: '600' } },
                        border: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}

// Risk Analysis (Price vs Volatility Scatter)
async function fetchRiskAnalysis() {
    const res = await fetch(`${API_BASE}/stocks`);
    const stocks = await res.json();

    const scatterData = stocks.map(s => ({
        x: s.volatility,
        y: s.price,
        label: s.symbol
    }));

    const ctx = document.getElementById('riskScatterChart');
    if (ctx) {
        if (window.riskScatterChartInstance) window.riskScatterChartInstance.destroy();

        window.riskScatterChartInstance = new Chart(ctx.getContext('2d'), {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Stocks',
                    data: scatterData,
                    backgroundColor: 'rgba(244, 63, 94, 0.6)', /* Rose-500 */
                    borderColor: '#f43f5e',
                    borderWidth: 1,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: 'Volatility (Risk)', color: '#94a3b8', font: { family: 'Inter' } },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    y: {
                        title: { display: true, text: 'Price ($)', color: '#94a3b8', font: { family: 'Inter' } },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#94a3b8' }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#e2e8f0',
                        bodyColor: '#e2e8f0',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderWidth: 1,
                        padding: 10,
                        callbacks: {
                            label: function (context) {
                                const point = context.raw;
                                return `${point.label}: $${point.y.toFixed(2)} (Vol: ${point.x})`;
                            }
                        }
                    }
                }
            }
        });
    }
}

// Full Sector Details (Chart + Deep Table + Dropdown Population)
async function fetchSectorDetails() {
    const res = await fetch(`${API_BASE}/sectors`);
    const data = await res.json();

    // Populate Dropdown
    const select = document.getElementById('sectorSelect');
    if (select && select.options.length <= 1) { // Only populate if empty
        data.forEach(s => {
            const option = document.createElement('option');
            option.value = s.sector;
            option.textContent = s.sector;
            select.appendChild(option);
        });
    }

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

// Fetch Sector Stocks (Sector Explorer)
async function fetchSectorStocks() {
    const sector = document.getElementById('sectorSelect').value;
    const criteria = document.getElementById('sortCriteria').value;
    const direction = document.getElementById('rankingDirection').value;

    const tbody = document.getElementById('sectorExplorerTableBody');

    if (!sector) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: var(--text-secondary);">Select a sector to view stocks</td></tr>';
        return;
    }

    // Use the stocks API with filtering, sorting, and LIMIT 5
    const res = await fetch(`${API_BASE}/stocks?sector=${sector}&sort=${criteria}&order=${direction}&limit=5`);
    const stocks = await res.json();

    // Update headers based on view
    const thead = document.querySelector('.sector-explorer-table thead tr');
    if (criteria === 'score') {
        thead.innerHTML = `
            <th>Symbol</th>
            <th>Name</th>
            <th>Price</th>
            <th>Volume</th>
            <th>Score</th>
        `;
    } else {
        thead.innerHTML = `
            <th>Symbol</th>
            <th>Name</th>
            <th>Price</th>
            <th>Volume</th>
            <th>Volatility</th>
        `;
    }

    tbody.innerHTML = '';

    if (stocks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: var(--text-secondary);">No stocks found in this sector</td></tr>';
        return;
    }

    stocks.forEach(s => {
        const tr = document.createElement('tr');
        let lastCell = `<td>${s.volatility}</td>`;
        if (criteria === 'score') {
            lastCell = `<td style="font-weight:bold; color:var(--accent)">${s.score ? s.score.toFixed(2) : 'N/A'}</td>`;
        }

        tr.innerHTML = `
            <td style="font-weight: bold; color: var(--accent)">${s.symbol}</td>
            <td>${s.name}</td>
            <td>$${s.price.toFixed(2)}</td>
            <td>${s.volume.toLocaleString()}</td>
            ${lastCell}
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

// ============================================
// REAL-TIME UPDATE FUNCTIONS
// ============================================

function startRealTimeUpdates() {
    console.log("Starting real-time updates...");

    // Update every 5 seconds
    updateInterval = setInterval(async () => {
        if (isUpdating) {
            await updateAllCharts();
        }
    }, 5000);
}

function stopRealTimeUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
    console.log("Stopped real-time updates");
}

async function updateAllCharts() {
    try {
        // Show update indicator
        showUpdateIndicator(true);

        // Fetch all data and update charts
        await Promise.all([
            fetchSentiment(),
            fetchTopK(),
            fetchSectors(),
            fetchTopCharts(),
            fetchRiskAnalysis()
        ]);

        // Update timestamp
        await updateTimestamp();

        // Hide update indicator
        setTimeout(() => showUpdateIndicator(false), 500);

    } catch (error) {
        console.error("Error updating charts:", error);
        showUpdateIndicator(false);
    }
}

function showUpdateIndicator(show) {
    const indicator = document.getElementById('liveIndicator');
    if (indicator) {
        if (show) {
            indicator.classList.add('pulsing');
        } else {
            indicator.classList.remove('pulsing');
        }
    }
}

async function updateTimestamp() {
    try {
        const res = await fetch(`${API_BASE}/last-update`);
        const data = await res.json();

        const timestampEl = document.getElementById('lastUpdateTime');
        if (timestampEl) {
            timestampEl.textContent = data.timestamp;
        }

        lastDataVersion = data.version;
    } catch (error) {
        console.error("Error fetching timestamp:", error);
    }
}

function toggleUpdates() {
    isUpdating = !isUpdating;
    const btn = document.getElementById('toggleUpdateBtn');
    if (btn) {
        if (isUpdating) {
            btn.textContent = '⏸ Pause Updates';
            btn.classList.remove('paused');
        } else {
            btn.textContent = '▶ Resume Updates';
            btn.classList.add('paused');
        }
    }
}
