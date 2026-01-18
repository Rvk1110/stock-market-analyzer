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
// Sentiment Chart
async function fetchSentiment() {
    const res = await fetch(`${API_BASE}/sentiment`);
    const data = await res.json();

    const ctx = document.getElementById('sentimentChart').getContext('2d');

    if (window.sentimentChartInstance) window.sentimentChartInstance.destroy();

    window.sentimentChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Up', 'Down', 'Stable'],
            datasets: [{
                data: [data.UP || 0, data.DOWN || 0, data.STABLE || 0],
                backgroundColor: ['#10b981', '#ef4444', '#6b7280'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#bbb' } }
            }
        }
    });
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

        window.sectorPriceChartInstance = new Chart(priceCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Avg Price ($)',
                    data: prices,
                    backgroundColor: 'rgba(99, 102, 241, 0.6)',
                    borderColor: '#6366f1',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#bbb' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#bbb' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // 2. Sector Volume Pie Chart
    const volumeCtx = document.getElementById('sectorVolumeChart');
    if (volumeCtx) {
        if (window.sectorVolumeChartInstance) window.sectorVolumeChartInstance.destroy();

        const labels = data.map(s => s.sector);
        const volumes = data.map(s => s.total_volume);

        window.sectorVolumeChartInstance = new Chart(volumeCtx.getContext('2d'), {
            type: 'pie',
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
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#bbb', font: { size: 10 } }
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
        if (window.topPriceChartInstance) window.topPriceChartInstance.destroy();

        window.topPriceChartInstance = new Chart(priceCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: priceData.map(s => s.symbol),
                datasets: [{
                    label: 'Price ($)',
                    data: priceData.map(s => s.price),
                    backgroundColor: 'rgba(16, 185, 129, 0.6)',
                    borderColor: '#10b981',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#bbb' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#bbb' }
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
        if (window.topVolumeChartInstance) window.topVolumeChartInstance.destroy();

        window.topVolumeChartInstance = new Chart(volumeCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: volumeData.map(s => s.symbol),
                datasets: [{
                    label: 'Volume',
                    data: volumeData.map(s => s.volume),
                    backgroundColor: 'rgba(245, 158, 11, 0.6)',
                    borderColor: '#f59e0b',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#bbb' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#bbb' }
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
                    backgroundColor: 'rgba(236, 72, 153, 0.6)',
                    borderColor: '#ec4899',
                    borderWidth: 1,
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: 'Volatility', color: '#bbb' },
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#bbb' }
                    },
                    y: {
                        title: { display: true, text: 'Price ($)', color: '#bbb' },
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#bbb' }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const point = context.raw;
                                return `${point.label}: $${point.y.toFixed(2)}, Vol: ${point.x}`;
                            }
                        }
                    }
                }
            }
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
