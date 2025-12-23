// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const raceSelect = document.getElementById('race-select');
const loadButton = document.getElementById('load-button');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const errorText = document.getElementById('error-text');
const resultsContainer = document.getElementById('results-container');
const emptyState = document.getElementById('empty-state');
const resultsTitle = document.getElementById('results-title');
const resultsSubtitle = document.getElementById('results-subtitle');
const resultsCount = document.getElementById('results-count');
const tableHead = document.getElementById('table-head');
const tableBody = document.getElementById('table-body');
const summaryCards = document.getElementById('summary-cards');
const searchInput = document.getElementById('search-input');
const sortSelect = document.getElementById('sort-select');

// State
let races = [];
let currentResults = null;
let filteredResults = null;

// Initialize the application
async function init() {
    try {
        await loadRaces();
    } catch (error) {
        showError('Failed to initialize application: ' + error.message);
    }
}

// Load available races
async function loadRaces() {
    try {
        const response = await fetch(`${API_BASE_URL}/races`);
        if (!response.ok) throw new Error('Failed to fetch races');
        
        const data = await response.json();
        races = data.races || [];
        
        // Populate select dropdown
        raceSelect.innerHTML = '';
        if (races.length === 0) {
            raceSelect.innerHTML = '<option value="">No races available</option>';
            loadButton.disabled = true;
        } else {
            raceSelect.innerHTML = '<option value="">-- Select a race --</option>';
            races.forEach(race => {
                const option = document.createElement('option');
                option.value = race.url;
                option.textContent = race.carrera;
                raceSelect.appendChild(option);
            });
            loadButton.disabled = false;
        }
    } catch (error) {
        console.error('Error loading races:', error);
        raceSelect.innerHTML = '<option value="">Error loading races</option>';
        loadButton.disabled = true;
        throw error;
    }
}

// Load race results
async function loadResults() {
    const selectedUrl = raceSelect.value;
    if (!selectedUrl) {
        showError('Please select a race');
        return;
    }

    // Show loading state
    hideAll();
    loadingDiv.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/results`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: selectedUrl })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to fetch results');
        }

        const data = await response.json();
        currentResults = data.results;

        if (!currentResults || currentResults.length === 0) {
            showError('No results found for this race');
            return;
        }

        displayResults(currentResults);
    } catch (error) {
        console.error('Error loading results:', error);
        
        // Check if it's a 404 error (no results found)
        if (error.message.includes('No results found')) {
            showError('⚠️ No hay resultados disponibles para esta carrera. Puede ser una carrera futura o los datos aún no están disponibles en ProCyclingStats.');
        } else {
            showError('❌ Error al cargar los resultados: ' + error.message);
        }
    }
}

// Display results in table
function displayResults(results) {
    hideAll();
    currentResults = results;
    filteredResults = [...results];

    // Get column names from first result
    const columns = Object.keys(results[0]);

    // Create summary cards
    displaySummaryCards(results, columns);

    // Create table header
    tableHead.innerHTML = '';
    const headerRow = document.createElement('tr');
    columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = formatColumnName(col);
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => sortByColumn(col));
        headerRow.appendChild(th);
    });
    tableHead.appendChild(headerRow);

    // Populate sort select
    sortSelect.innerHTML = '<option value="">Sort by...</option>';
    columns.forEach(col => {
        const option = document.createElement('option');
        option.value = col;
        option.textContent = formatColumnName(col);
        sortSelect.appendChild(option);
    });

    // Create table body
    renderTableBody(filteredResults, columns);

    // Update results info
    const selectedRace = races.find(r => r.url === raceSelect.value);
    resultsTitle.textContent = selectedRace ? selectedRace.carrera : 'Race Results';
    resultsSubtitle.textContent = `${results.length} total results`;
    resultsCount.textContent = `${filteredResults.length} shown`;

    // Show results container
    resultsContainer.classList.remove('hidden');
}

// Display summary cards
function displaySummaryCards(results, columns) {
    summaryCards.innerHTML = '';
    
    // Total results
    const totalCard = document.createElement('div');
    totalCard.className = 'summary-card';
    totalCard.innerHTML = `
        <div class="summary-card-label">Total Results</div>
        <div class="summary-card-value">${results.length}</div>
    `;
    summaryCards.appendChild(totalCard);

    // Numeric columns stats
    columns.forEach(col => {
        const values = results
            .map(r => r[col])
            .filter(v => v !== null && v !== undefined && !isNaN(v));
        
        if (values.length > 0 && typeof values[0] === 'number') {
            const max = Math.max(...values);
            const card = document.createElement('div');
            card.className = 'summary-card';
            card.innerHTML = `
                <div class="summary-card-label">${formatColumnName(col)}</div>
                <div class="summary-card-value">${max}</div>
            `;
            summaryCards.appendChild(card);
        }
    });
}

// Render table body with filtering
function renderTableBody(results, columns) {
    tableBody.innerHTML = '';
    results.forEach((result) => {
        const row = document.createElement('tr');
        columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = result[col] !== null && result[col] !== undefined ? result[col] : '-';
            row.appendChild(td);
        });
        tableBody.appendChild(row);
    });
    resultsCount.textContent = `${results.length} shown`;
}

// Format column names for display
function formatColumnName(name) {
    return name
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

// Sort by column
function sortByColumn(col) {
    const sorted = [...filteredResults].sort((a, b) => {
        const valA = a[col];
        const valB = b[col];
        
        if (valA === null || valA === undefined) return 1;
        if (valB === null || valB === undefined) return -1;
        
        if (typeof valA === 'number' && typeof valB === 'number') {
            return valB - valA;
        }
        return String(valA).localeCompare(String(valB));
    });
    
    filteredResults = sorted;
    const columns = Object.keys(currentResults[0]);
    renderTableBody(filteredResults, columns);
}

// Search/Filter results
function filterResults(query) {
    if (!currentResults) return;
    
    const q = query.toLowerCase();
    filteredResults = currentResults.filter(result => {
        return Object.values(result).some(val => 
            String(val).toLowerCase().includes(q)
        );
    });
    
    const columns = Object.keys(currentResults[0]);
    renderTableBody(filteredResults, columns);
}

// Show error message
function showError(message) {
    hideAll();
    errorText.textContent = message;
    errorDiv.classList.remove('hidden');
}

// Hide all result states
function hideAll() {
    loadingDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
    resultsContainer.classList.add('hidden');
    emptyState.classList.add('hidden');
}

// Show empty state
function showEmptyState() {
    hideAll();
    emptyState.classList.remove('hidden');
}

// Event Listeners
loadButton.addEventListener('click', loadResults);

raceSelect.addEventListener('change', () => {
    if (raceSelect.value) {
        loadButton.disabled = false;
    } else {
        loadButton.disabled = true;
    }
});

searchInput.addEventListener('input', (e) => {
    filterResults(e.target.value);
});

sortSelect.addEventListener('change', (e) => {
    if (e.target.value) {
        sortByColumn(e.target.value);
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    showEmptyState();
    init();
});
