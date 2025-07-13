// Configuration
const API_BASE_URL = 'http://localhost:8000';

console.log('🚀 listings.js loaded successfully!');

// Global variables
let allListings = [];
let filteredListings = [];

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing page...');
    
    // Show loading state immediately
    showLoadingState();
    
    // Check system status first
    checkSystemStatus();
    
    // Load listings with a slight delay to ensure everything is ready
    setTimeout(() => {
        loadListings();
    }, 500);
    
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterListings, 300));
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterListings);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', filterListings);
    }
}

// Debounce function to limit API calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Check system status
async function checkSystemStatus() {
    const statusIndicator = document.getElementById('statusIndicator');
    const systemStatus = document.getElementById('systemStatus');
    
    try {
        const response = await fetch(`${API_BASE_URL}/status`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            if (statusIndicator) statusIndicator.className = 'w-3 h-3 rounded-full bg-green-400 mr-2';
            if (systemStatus) systemStatus.textContent = 'Sistema Operativo';
        } else {
            throw new Error('Health check failed');
        }
    } catch (error) {
        console.error('Error checking system status:', error);
        if (statusIndicator) statusIndicator.className = 'w-3 h-3 rounded-full bg-red-400 mr-2';
        if (systemStatus) systemStatus.textContent = 'Sistema Desconectado';
    }
}

// Load all listings from the backend
async function loadListings() {
    console.log('Starting to load listings...');
    showLoadingState();
    
    try {
        console.log('Fetching from:', `${API_BASE_URL}/listings/`);
        
        const response = await fetch(`${API_BASE_URL}/listings/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Raw data received:', data);
        
        allListings = (data.listings || data || []).map(listing => ({
            ...listing,
            // Clean up category format
            category: listing.category ? listing.category.replace('ProductCategory.', '') : 'Sin categoría',
            // Ensure confidence_score is a number
            confidence_score: Number(listing.confidence_score || 0),
            // Ensure price is properly formatted
            price: listing.target_price || listing.price || null
        }));
        filteredListings = [...allListings];
        
        console.log('Processed listings:', allListings);
        console.log('Total listings:', allListings.length);
        
        updateStats();
        renderListings();
        
    } catch (error) {
        console.error('Error loading listings:', error);
        console.error('Error details:', error.message);
        showToast('Error al cargar los listings: ' + error.message, 'error');
        showEmptyState();
    }
}

// Show loading state
function showLoadingState() {
    console.log('showLoadingState called');
    const loadingEl = document.getElementById('loadingState');
    const emptyEl = document.getElementById('emptyState');
    const tableEl = document.getElementById('listingsTable');
    
    if (loadingEl) loadingEl.classList.remove('hidden');
    if (emptyEl) emptyEl.classList.add('hidden');
    if (tableEl) tableEl.classList.add('hidden');
}

// Show empty state
function showEmptyState() {
    console.log('showEmptyState called');
    const loadingEl = document.getElementById('loadingState');
    const emptyEl = document.getElementById('emptyState');
    const tableEl = document.getElementById('listingsTable');
    
    if (loadingEl) loadingEl.classList.add('hidden');
    if (emptyEl) emptyEl.classList.remove('hidden');
    if (tableEl) tableEl.classList.add('hidden');
}

// Show listings table
function showListingsTable() {
    console.log('showListingsTable called');
    const loadingEl = document.getElementById('loadingState');
    const emptyEl = document.getElementById('emptyState');
    const tableEl = document.getElementById('listingsTable');
    
    if (loadingEl) loadingEl.classList.add('hidden');
    if (emptyEl) emptyEl.classList.add('hidden');
    if (tableEl) tableEl.classList.remove('hidden');
}

// Update statistics cards
function updateStats() {
    const totalListings = allListings.length;
    const publishedListings = allListings.filter(listing => listing.status === 'published').length;
    const draftListings = allListings.filter(listing => listing.status === 'draft').length;
    
    // Calculate average confidence
    const avgConfidence = totalListings > 0 
        ? Math.round(allListings.reduce((sum, listing) => sum + (listing.confidence_score || 0), 0) / totalListings)
        : 0;
    
    const totalEl = document.getElementById('totalListings');
    const publishedEl = document.getElementById('publishedListings');
    const draftEl = document.getElementById('draftListings');
    const avgEl = document.getElementById('avgConfidence');
    
    if (totalEl) totalEl.textContent = totalListings;
    if (publishedEl) publishedEl.textContent = publishedListings;
    if (draftEl) draftEl.textContent = draftListings;
    if (avgEl) avgEl.textContent = `${avgConfidence}%`;
}

// Render listings in the table
function renderListings() {
    console.log('renderListings called');
    console.log('filteredListings length:', filteredListings.length);
    console.log('allListings length:', allListings.length);
    
    if (filteredListings.length === 0) {
        console.log('No filtered listings found');
        if (allListings.length === 0) {
            console.log('No listings at all, showing empty state');
            showEmptyState();
        } else {
            console.log('Has listings but filtered out, showing no results message');
            showListingsTable();
            const tbody = document.getElementById('listingsTableBody');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" class="px-6 py-8 text-center text-gray-500">
                            <i class="fas fa-search text-2xl mb-2"></i>
                            <p>No se encontraron listings con los filtros aplicados</p>
                        </td>
                    </tr>
                `;
            }
        }
        return;
    }
    
    console.log('Showing listings table with', filteredListings.length, 'listings');
    showListingsTable();
    
    const tbody = document.getElementById('listingsTableBody');
    if (!tbody) {
        console.error('No se encontró el tbody de la tabla');
        return;
    }
    
    // Debug: log the first listing to see its structure
    if (filteredListings.length > 0) {
        console.log('First listing structure:', filteredListings[0]);
    }
    
    try {
        tbody.innerHTML = filteredListings.map((listing, index) => {
            console.log(`Processing listing ${index + 1}:`, listing.id || 'no-id', listing.product_name || 'no-name');
            
            return generateListingRow(listing);
        }).join('');
        
        console.log('✅ Table rendered successfully');
    } catch (error) {
        console.error('Error rendering table:', error);
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="px-6 py-8 text-center text-red-500">
                    <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                    <p>Error al renderizar la tabla: ${error.message}</p>
                </td>
            </tr>
        `;
    }
}

// Generate listing row HTML
function generateListingRow(listing) {
    const listingId = listing.id || 'unknown';
    const productName = escapeHtml(listing.product_name || 'Sin nombre');
    const title = escapeHtml(truncateText(listing.title || 'Sin título', 50));
    const category = escapeHtml(listing.category || 'Sin categoría');
    const price = listing.price ? `$${parseFloat(listing.price).toFixed(2)}` : 'No definido';
    const confidence = listing.confidence_score || 0;
    const status = listing.status || 'draft';
    const createdAt = formatDate(listing.created_at);
    
    return `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                        <div class="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                            <i class="fas fa-box text-white"></i>
                        </div>
                    </div>
                    <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">${productName}</div>
                        <div class="text-sm text-gray-500">${title}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    ${category}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${price}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                        <div class="h-2 rounded-full ${getConfidenceColor(confidence)}" 
                             style="width: ${confidence}%"></div>
                    </div>
                    <span class="text-sm text-gray-600">${confidence}%</span>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(status)}">
                    ${getStatusText(status)}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${createdAt}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                    <button onclick="viewListing('${listingId}')" 
                            class="text-blue-600 hover:text-blue-900 transition-colors"
                            title="Ver detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="editListing('${listingId}')" 
                            class="text-green-600 hover:text-green-900 transition-colors"
                            title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="duplicateListing('${listingId}')" 
                            class="text-purple-600 hover:text-purple-900 transition-colors"
                            title="Duplicar">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button onclick="deleteListing('${listingId}')" 
                            class="text-red-600 hover:text-red-900 transition-colors"
                            title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `;
}

// Filter listings based on search and filters
function filterListings() {
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    const categoryValue = categoryFilter ? categoryFilter.value : '';
    const statusValue = statusFilter ? statusFilter.value : '';
    
    filteredListings = allListings.filter(listing => {
        const matchesSearch = !searchTerm || 
            (listing.product_name && listing.product_name.toLowerCase().includes(searchTerm)) ||
            (listing.title && listing.title.toLowerCase().includes(searchTerm)) ||
            (listing.description && listing.description.toLowerCase().includes(searchTerm));
        
        const matchesCategory = !categoryValue || listing.category === categoryValue;
        const matchesStatus = !statusValue || listing.status === statusValue;
        
        return matchesSearch && matchesCategory && matchesStatus;
    });
    
    renderListings();
}

// Action functions
function viewListing(listingId) {
    console.log('👁️ View listing:', listingId);
    window.location.href = `listing-details.html?id=${listingId}`;
}

function editListing(listingId) {
    console.log('✏️ Edit listing:', listingId);
    window.location.href = `edit-listing.html?id=${listingId}`;
}

async function duplicateListing(listingId) {
    console.log('📋 Duplicate listing:', listingId);
    
    if (!confirm('¿Quieres crear una copia de este listing?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/listings/${listingId}/duplicate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        showToast('Listing duplicado exitosamente', 'success');
        
        // Reload listings after short delay
        setTimeout(() => {
            loadListings();
        }, 1000);
        
    } catch (error) {
        console.error('Error duplicating listing:', error);
        showToast(`Error al duplicar listing: ${error.message}`, 'error');
    }
}

async function deleteListing(listingId) {
    console.log('🗑️ Delete listing:', listingId);
    
    if (!confirm('¿Estás seguro de que quieres eliminar este listing? Esta acción no se puede deshacer.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/listings/${listingId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        showToast('Listing eliminado exitosamente', 'success');
        
        // Reload listings after short delay
        setTimeout(() => {
            loadListings();
        }, 1000);
        
    } catch (error) {
        console.error('Error deleting listing:', error);
        showToast(`Error al eliminar listing: ${error.message}`, 'error');
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function getConfidenceColor(confidence) {
    if (confidence >= 80) return 'bg-green-500';
    if (confidence >= 60) return 'bg-yellow-500';
    if (confidence >= 40) return 'bg-orange-500';
    return 'bg-red-500';
}

function getStatusBadge(status) {
    switch(status) {
        case 'published': return 'bg-green-100 text-green-800';
        case 'draft': return 'bg-yellow-100 text-yellow-800';
        case 'archived': return 'bg-gray-100 text-gray-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

function getStatusText(status) {
    switch(status) {
        case 'published': return 'Publicado';
        case 'draft': return 'Borrador';
        case 'archived': return 'Archivado';
        default: return 'Borrador';
    }
}

function formatDate(dateString) {
    if (!dateString) return 'No definido';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return 'Fecha inválida';
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    if (!toast || !toastMessage) return;
    
    // Set message
    toastMessage.textContent = message;
    
    // Set style based on type
    let bgColor;
    switch(type) {
        case 'success': bgColor = 'bg-green-500 text-white'; break;
        case 'error': bgColor = 'bg-red-500 text-white'; break;
        case 'warning': bgColor = 'bg-yellow-500 text-white'; break;
        default: bgColor = 'bg-blue-500 text-white'; break;
    }
    
    toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300 ${bgColor}`;
    
    // Show toast
    toast.classList.remove('hidden', 'translate-y-full');
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('translate-y-full');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 300);
    }, 3000);
}
