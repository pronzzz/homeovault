const API_URL = '/api';

// --- Store Name Logic ---
function editStoreName() {
    const current = localStorage.getItem('storeName') || "HomeoVault";
    const newName = prompt("Enter your Shop/Clinic Name:", current);

    if (newName && newName.trim() !== "") {
        localStorage.setItem('storeName', newName.trim());
        updateTitle(newName.trim());
    }
}

function updateTitle(name) {
    document.getElementById('app-title').innerHTML = `${name} <span>💊</span>`;
    document.title = `${name} - Inventory`;
}

// Load Store Name on Start
const savedName = localStorage.getItem('storeName');
if (savedName) updateTitle(savedName);

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    fetchMedicines();
    setupEventListeners();
    // Health check loop
    setInterval(checkHealth, 5000);
});

function setupEventListeners() {
    // Modal Toggles
    document.getElementById('add-btn').addEventListener('click', () => openModal('add-modal'));

    // Form Submission
    document.getElementById('add-form').addEventListener('submit', handleAddStock);
}

// --- Health Check ---
async function checkHealth() {
    const indicator = document.getElementById('status-indicator');
    try {
        const res = await fetch(`${API_URL}/health`);
        if (res.ok) {
            indicator.textContent = "System Online";
            indicator.className = "status-ok";
        } else {
            throw new Error("Server error");
        }
    } catch (e) {
        indicator.textContent = "Offline / Connection Lost";
        indicator.className = "status-error";
    }
}

// --- Core Data Logic ---
async function fetchMedicines() {
    const container = document.getElementById('items-container');
    container.innerHTML = '<div class="loading">Loading inventory...</div>';

    try {
        const res = await fetch(`${API_URL}/medicines`);
        if (!res.ok) throw new Error("Failed to fetch");
        const medicines = await res.json();
        renderMedicines(medicines);
        updateStats(medicines);
    } catch (err) {
        console.error(err);
        container.innerHTML = '<div class="error-message">Could not load inventory. Check server connection.</div>';
    }
}

function renderMedicines(medicines) {
    const container = document.getElementById('items-container');
    container.innerHTML = '';

    if (medicines.length === 0) {
        container.innerHTML = '<div class="empty-state">No medicines found. Click "+ Add Stock" to begin.</div>';
        return;
    }

    medicines.forEach(med => {
        const card = document.createElement('div');
        card.className = 'item-card';

        // Check expiry status
        const today = new Date().toISOString().split('T')[0];
        const isExpired = med.expiry_date < today;

        // Calculate days to expiry
        const daysToExpiry = Math.ceil((new Date(med.expiry_date) - new Date()) / (1000 * 60 * 60 * 24));
        let expiryClass = 'status-expiry';
        let expiryText = `Exp: ${med.expiry_date}`;

        if (isExpired) {
            expiryClass += ' expired';
            expiryText = `EXPIRED (${med.expiry_date})`;
        } else if (daysToExpiry <= 60) {
            expiryClass += ' near';
            expiryText = `Expiring Soon (${med.expiry_date})`;
        }

        card.innerHTML = `
            <div class="item-info">
                <h3>${med.medicine_name} <span class="sku-badge">${med.potency}</span></h3>
                <div class="details">
                    <span class="sku-badge">${med.form}</span>
                    <span class="sku-badge">${med.bottle_size}</span>
                    <span class="sku-badge">${med.manufacturer}</span>
                </div>
                <div class="batch-info">
                    Batch: <strong>${med.batch_number}</strong> | 
                    <span class="${expiryClass}">${expiryText}</span>
                </div>
                <div class="price-info" style="margin-top: 5px; color: #555;">
                     MRP: ₹${med.mrp} | Stock: <strong>${med.quantity}</strong>
                </div>
            </div>
            <div class="item-actions">
                <button class="qty-btn minus" onclick="sellMedicine(${med.id}, '${med.medicine_name}', ${isExpired})">SELL</button>
                <button class="delete-btn" onclick="deleteMedicine(${med.id})">🗑️</button>
            </div>
        `;
        container.appendChild(card);
    });
}

function updateStats(medicines) {
    const today = new Date().toISOString().split('T')[0];

    const totalMedicines = medicines.length;
    const totalBottles = medicines.reduce((sum, m) => sum + m.quantity, 0);
    const expiredCount = medicines.filter(m => m.expiry_date < today).length;
    const lowStockCount = medicines.filter(m => m.quantity <= m.low_stock_threshold).length;

    document.getElementById('total-medicines').textContent = totalMedicines;
    document.getElementById('total-bottles').textContent = totalBottles;
    document.getElementById('expired-count').textContent = expiredCount;
    document.getElementById('low-stock-count').textContent = lowStockCount;

    // Visual Alerts
    document.querySelector('.stat-card.expired').style.opacity = expiredCount > 0 ? '1' : '0.7';
    document.querySelector('.stat-card.low-stock').style.opacity = lowStockCount > 0 ? '1' : '0.7';
}

// --- Action Handlers ---

async function handleAddStock(e) {
    e.preventDefault();
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = "Saving...";

    const data = {
        medicine_name: document.getElementById('med-name').value,
        potency: document.getElementById('med-potency').value,
        form: document.getElementById('med-form').value,
        bottle_size: document.getElementById('med-size').value,
        manufacturer: document.getElementById('med-manuf').value,
        batch_number: document.getElementById('med-batch').value,
        expiry_date: document.getElementById('med-expiry').value,
        mrp: parseFloat(document.getElementById('med-mrp').value),
        purchase_price: parseFloat(document.getElementById('med-price').value),
        quantity: parseInt(document.getElementById('med-qty').value),
        low_stock_threshold: parseInt(document.getElementById('med-threshold').value)
    };

    try {
        const res = await fetch(`${API_URL}/medicines`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (res.ok) {
            closeModal();
            fetchMedicines();
            document.getElementById('add-form').reset();
            alert("Stock Added Successfully!");
        } else {
            alert("Error: " + (result.detail || "Unknown error"));
        }
    } catch (err) {
        alert("Connection Failed");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Save Stock";
    }
}

async function sellMedicine(id, name, isExpired) {
    let note = "Sold via Quick Sell";

    if (isExpired) {
        if (!confirm(`WARNING: ${name} is EXPIRED! Do you really want to sell it?`)) {
            return;
        }
        note += " [OVERRIDE EXPIRED]";
    }

    try {
        const res = await fetch(`${API_URL}/transaction`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                medicine_id: id,
                change_amount: -1,
                action_type: "SELL",
                note: note
            })
        });

        if (res.ok) {
            fetchMedicines(); // Refresh UI
        } else {
            const err = await res.json();
            alert("Sale Failed: " + err.detail);
        }
    } catch (e) {
        alert("Network Error during sale");
    }
}

async function deleteMedicine(id) {
    if (!confirm("Are you sure? This will delete the medicine record permanently.")) return;

    try {
        const res = await fetch(`${API_URL}/medicines/${id}`, { method: 'DELETE' });
        if (res.ok) fetchMedicines();
        else alert("Delete failed");
    } catch (e) {
        alert("Network error");
    }
}

// --- Reports Logic ---
async function showReports() {
    openModal('reports-modal');
    document.getElementById('report-expired').innerHTML = 'Loading...';
    document.getElementById('report-low').innerHTML = 'Loading...';

    try {
        const res = await fetch(`${API_URL}/medicines`);
        const medicines = await res.json();

        const today = new Date().toISOString().split('T')[0];

        // Expired Report
        const expired = medicines.filter(m => {
            const daysToExpiry = Math.ceil((new Date(m.expiry_date) - new Date()) / (1000 * 60 * 60 * 24));
            return m.expiry_date < today || daysToExpiry <= 60;
        });

        if (expired.length === 0) {
            document.getElementById('report-expired').innerHTML = '<p class="status-ok">No expired or near-expiry items.</p>';
        } else {
            let html = '<table class="report-table"><thead><tr><th>Name</th><th>Batch</th><th>Expiry</th><th>Qty</th></tr></thead><tbody>';
            expired.forEach(m => {
                const isExp = m.expiry_date < today;
                const style = isExp ? 'color:red; font-weight:bold;' : 'color:orange;';
                html += `<tr>
                    <td>${m.medicine_name} (${m.potency})</td>
                    <td>${m.batch_number}</td>
                    <td style="${style}">${m.expiry_date}</td>
                    <td>${m.quantity}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            document.getElementById('report-expired').innerHTML = html;
        }

        // Low Stock Report
        const low = medicines.filter(m => m.quantity <= m.low_stock_threshold);
        if (low.length === 0) {
            document.getElementById('report-low').innerHTML = '<p class="status-ok">Stock levels are healthy.</p>';
        } else {
            let html = '<table class="report-table"><thead><tr><th>Name</th><th>Threshold</th><th>Current</th></tr></thead><tbody>';
            low.forEach(m => {
                html += `<tr>
                    <td>${m.medicine_name} (${m.potency})</td>
                    <td>${m.low_stock_threshold}</td>
                    <td style="color:red; font-weight:bold;">${m.quantity}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            document.getElementById('report-low').innerHTML = html;
        }

    } catch (e) {
        document.getElementById('report-expired').innerHTML = 'Error loading data.';
        document.getElementById('report-low').innerHTML = 'Error loading data.';
    }
}

// --- History Logic ---
async function showHistory() {
    const list = document.getElementById('history-list');
    list.innerHTML = 'Loading...';
    openModal('history-modal');

    try {
        const res = await fetch(`${API_URL}/history`);
        const data = await res.json();
        list.innerHTML = '';

        if (data.length === 0) {
            list.innerHTML = '<p>No transactions yet.</p>';
            return;
        }

        data.forEach(txn => {
            const row = document.createElement('div');
            row.className = 'history-item';
            const time = new Date(txn.timestamp).toLocaleString();
            const color = txn.change > 0 ? 'green' : 'red';
            const sign = txn.change > 0 ? '+' : '';

            row.innerHTML = `
                <div>
                    <strong>${txn.medicine_name}</strong> (${txn.batch_number})<br>
                    <small>${time} - ${txn.note || ''}</small>
                </div>
                <div style="font-weight:bold; color:${color}">
                    ${sign}${txn.change}
                </div>
            `;
            list.appendChild(row);
        });

    } catch (e) {
        list.innerHTML = '<p>Error loading history.</p>';
    }
}

function closeHistory() {
    closeModal();
}

// --- Modal Helpers ---
function openModal(id) {
    document.getElementById(id).classList.remove('hidden');
    document.getElementById(id).classList.add('active');
}

function closeModal() {
    document.querySelectorAll('.modal').forEach(m => {
        m.classList.remove('active');
        m.classList.add('hidden');
    });
}
window.closeModal = closeModal; // Expose to global for button onclicks

// Search Filter
window.filterItems = function () {
    const term = document.getElementById('search-box').value.toLowerCase();
    const items = document.querySelectorAll('.item-card');
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(term) ? 'grid' : 'none';
    });
}
