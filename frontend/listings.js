// Configuration - API Base URL dinámica
const API_BASE_URL = (() => {
    // La API siempre está en el puerto 8000
    const apiPort = '8000';
    const currentHost = window.location.hostname || 'localhost';
    const currentProtocol = window.location.protocol || 'http:';
    return `${currentProtocol}//${currentHost}:${apiPort}`;
})();

console.log('API Base URL configurada dinámicamente:', API_BASE_URL);
console.log('🚀 listings.js loaded successfully!');

// Global variables
let allListings = [];
let filteredListings = [];

// Show toast notification - moved to top for availability
function showToast(message, type = 'info') {
    try {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        
        if (!toast || !toastMessage) {
            console.warn('Toast elements not found in DOM');
            return;
        }
        
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
        
        console.log('Toast shown:', { message, type });
    } catch (error) {
        console.error('Error showing toast:', error);
        // Fallback to console.log if toast fails
        console.log(`Toast (${type}): ${message}`);
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing page...', {
        readyState: document.readyState,
        location: window.location.href
    });
    
    // Verify required elements exist
    const requiredElements = ['totalListings', 'publishedListings', 'draftListings', 'toast', 'toastMessage'];
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    if (missingElements.length > 0) {
        console.error('Missing required elements:', missingElements);
    }
    
    try {
        // Show loading state immediately
        showLoadingState();
        
        // Setup event listeners
        setupEventListeners();
        
        // Check system status first (but don't wait for it)
        checkSystemStatus().catch(error => {
            console.warn('System status check failed, but continuing:', error);
        });
        
        // Load listings immediately, don't wait for anything else
        console.log('Starting listings load immediately...');
        loadListings().catch(error => {
            console.error('Failed to load listings:', error);
            showEmptyState();
        });
    } catch (error) {
        console.error('Error during page initialization:', error);
        showEmptyState();
    }
});

// Setup event listeners
function setupEventListeners() {
    console.log('🔧 Setting up event listeners...');
    
    try {
        const searchInput = document.getElementById('searchInput');
        const categoryFilter = document.getElementById('categoryFilter');
        const statusFilter = document.getElementById('statusFilter');
        
        console.log('🔍 DOM elements found:', {
            searchInput: !!searchInput,
            categoryFilter: !!categoryFilter,
            statusFilter: !!statusFilter
        });
        
        if (searchInput) {
            searchInput.addEventListener('input', debounce(filterListings, 300));
            console.log('✅ Search input listener added');
        } else {
            console.warn('❌ searchInput element not found');
        }
        
        if (categoryFilter) {
            categoryFilter.addEventListener('change', filterListings);
            console.log('✅ Category filter listener added');
        } else {
            console.warn('❌ categoryFilter element not found');
        }
        
        if (statusFilter) {
            statusFilter.addEventListener('change', filterListings);
            console.log('✅ Status filter listener added');
        } else {
            console.warn('❌ statusFilter element not found');
        }
        
        console.log('✅ Event listeners setup complete');
    } catch (error) {
        console.error('❌ Error setting up event listeners:', error);
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
        // Use a simple endpoint that we know exists
        const response = await fetch(`${API_BASE_URL}/docs`, {
            method: 'HEAD'  // Just check if server is responding
        });
        
        if (response.ok || response.status === 200) {
            if (statusIndicator) statusIndicator.className = 'w-3 h-3 rounded-full bg-green-400 mr-2';
            if (systemStatus) systemStatus.textContent = 'Sistema Operativo';
        } else {
            throw new Error('Health check failed');
        }
    } catch (error) {
        console.error('Error checking system status:', error);
        if (statusIndicator) statusIndicator.className = 'w-3 h-3 rounded-full bg-red-400 mr-2';
        if (systemStatus) systemStatus.textContent = 'Sistema Desconectado';
        // Don't let this error prevent loading listings
    }
}

// Load all listings from the backend
async function loadListings() {
    console.log('🚀 Starting to load listings...');
    showLoadingState();
    
    try {
        console.log('📡 Fetching from:', `${API_BASE_URL}/api/listings/`);
        
        const response = await fetch(`${API_BASE_URL}/api/listings/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('📦 Response received. Status:', response.status, 'OK:', response.ok);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        console.log('🔄 Parsing JSON...');
        const data = await response.json();
        console.log('✅ Raw data received:', {
            dataType: typeof data,
            hasListings: !!data.listings,
            listingsLength: data.listings ? data.listings.length : 0,
            total: data.total
        });
        
        console.log('🔄 Processing listings...');
        allListings = (data.listings || data || []).map(listing => ({
            ...listing,
            // Clean up category format and convert to proper format
            category: listing.category ? 
                formatCategoryName(listing.category.replace('ProductCategory.', '')) : 
                'Sin categoría',
            // Ensure confidence_score is a number
            confidence_score: Number(listing.confidence_score || 0),
            // Ensure price is properly formatted (use target_price from API)
            price: listing.target_price || listing.price || 0
        }));
        filteredListings = [...allListings];
        
        console.log('✅ Processed listings:', {
            allListingsLength: allListings.length,
            filteredListingsLength: filteredListings.length,
            firstListing: allListings[0] ? {
                id: allListings[0].id,
                name: allListings[0].product_name,
                category: allListings[0].category,
                status: allListings[0].status
            } : null
        });
        
        // Debug: Log all unique categories and statuses
        if (allListings.length > 0) {
            const uniqueCategories = [...new Set(allListings.map(l => l.category))];
            const uniqueStatuses = [...new Set(allListings.map(l => l.status))];
            console.log('🏷️ Available categories:', uniqueCategories);
            console.log('🏷️ Available statuses:', uniqueStatuses);
        }
        
        console.log('🔄 Updating stats...');
        // Add a small delay to ensure DOM is fully ready
        setTimeout(() => {
            updateStats();
            populateFilterOptions();
        }, 10);
        
        console.log('🔄 Rendering listings...');
        renderListings();
        
        console.log('🎉 Listings loaded successfully!');
        
    } catch (error) {
        console.error('❌ Error loading listings:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack
        });
        showToast('Error al cargar los listings: ' + error.message, 'error');
        showEmptyState();
    }
}

// Show loading state
function showLoadingState() {
    console.log('showLoadingState called');
    try {
        const loadingEl = document.getElementById('loadingState');
        const emptyEl = document.getElementById('emptyState');
        const tableEl = document.getElementById('listingsTable');
        
        if (loadingEl) {
            loadingEl.classList.remove('hidden');
        } else {
            console.warn('loadingState element not found');
        }
        
        if (emptyEl) {
            emptyEl.classList.add('hidden');
        } else {
            console.warn('emptyState element not found');
        }
        
        if (tableEl) {
            tableEl.classList.add('hidden');
        } else {
            console.warn('listingsTable element not found');
        }
    } catch (error) {
        console.error('Error in showLoadingState:', error);
    }
}

// Show empty state
function showEmptyState() {
    console.log('showEmptyState called');
    try {
        const loadingEl = document.getElementById('loadingState');
        const emptyEl = document.getElementById('emptyState');
        const tableEl = document.getElementById('listingsTable');
        
        if (loadingEl) {
            loadingEl.classList.add('hidden');
        } else {
            console.warn('loadingState element not found');
        }
        
        if (emptyEl) {
            emptyEl.classList.remove('hidden');
        } else {
            console.warn('emptyState element not found');
        }
        
        if (tableEl) {
            tableEl.classList.add('hidden');
        } else {
            console.warn('listingsTable element not found');
        }
    } catch (error) {
        console.error('Error in showEmptyState:', error);
    }
}

// Show listings table
function showListingsTable() {
    console.log('showListingsTable called');
    try {
        const loadingEl = document.getElementById('loadingState');
        const emptyEl = document.getElementById('emptyState');
        const tableEl = document.getElementById('listingsTable');
        
        if (loadingEl) {
            loadingEl.classList.add('hidden');
        } else {
            console.warn('loadingState element not found');
        }
        
        if (emptyEl) {
            emptyEl.classList.add('hidden');
        } else {
            console.warn('emptyState element not found');
        }
        
        if (tableEl) {
            tableEl.classList.remove('hidden');
        } else {
            console.warn('listingsTable element not found');
        }
    } catch (error) {
        console.error('Error in showListingsTable:', error);
    }
}

// Update statistics cards
function updateStats() {
    try {
        const totalListings = allListings.length;
        const publishedListings = allListings.filter(listing => listing.status === 'published').length;
        const draftListings = allListings.filter(listing => listing.status === 'draft').length;
        
        const totalEl = document.getElementById('totalListings');
        const publishedEl = document.getElementById('publishedListings');
        const draftEl = document.getElementById('draftListings');
        
        if (totalEl) {
            totalEl.textContent = totalListings;
        } else {
            console.warn('Element totalListings not found');
        }
        
        if (publishedEl) {
            publishedEl.textContent = publishedListings;
        } else {
            console.warn('Element publishedListings not found');
        }
        
        if (draftEl) {
            draftEl.textContent = draftListings;
        } else {
            console.warn('Element draftListings not found');
        }
        
        console.log('Stats updated:', { totalListings, publishedListings, draftListings });
    } catch (error) {
        console.error('Error updating stats:', error);
    }
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
            const cardsContainer = document.getElementById('listingsCards');
            
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                            <i class="fas fa-search text-2xl mb-2"></i>
                            <p>No se encontraron listings con los filtros aplicados</p>
                        </td>
                    </tr>
                `;
            }
            
            if (cardsContainer) {
                cardsContainer.innerHTML = `
                    <div class="p-8 text-center text-gray-500">
                        <i class="fas fa-search text-2xl mb-2"></i>
                        <p>No se encontraron listings con los filtros aplicados</p>
                    </div>
                `;
            }
        }
        return;
    }
    
    console.log('Showing listings table with', filteredListings.length, 'listings');
    showListingsTable();
    
    // Render desktop table
    const tbody = document.getElementById('listingsTableBody');
    if (tbody) {
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
                    <td colspan="6" class="px-6 py-8 text-center text-red-500">
                        <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                        <p>Error al renderizar la tabla: ${error.message}</p>
                    </td>
                </tr>
            `;
        }
    }
    
    // Render mobile cards
    const cardsContainer = document.getElementById('listingsCards');
    if (cardsContainer) {
        try {
            cardsContainer.innerHTML = filteredListings.map((listing, index) => {
                console.log(`Processing card ${index + 1}:`, listing.id || 'no-id', listing.product_name || 'no-name');
                return generateListingCard(listing);
            }).join('');
            
            console.log('✅ Cards rendered successfully');
        } catch (error) {
            console.error('Error rendering cards:', error);
            cardsContainer.innerHTML = `
                <div class="p-8 text-center text-red-500">
                    <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                    <p>Error al renderizar las cards: ${error.message}</p>
                </div>
            `;
        }
    }
}

// Generate listing row HTML
// Generate listing row HTML - SIN COLUMNA DE CONFIANZA
function generateListingRow(listing) {
    const listingId = listing.id || 'unknown';
    const productName = escapeHtml(listing.product_name || 'Sin nombre');
    const title = escapeHtml(truncateText(listing.title || 'Sin título', 20));
    const category = escapeHtml(truncateText(listing.category || 'Sin categoría', 8));
    const price = listing.price ? `$${parseFloat(listing.price).toFixed(0)}` : 'N/A';
    const status = listing.status || 'draft';
    
    return `
        <tr class="hover:bg-gray-50">
            <td class="px-3 py-3 text-xs border">
                <div class="flex items-center">
                    <div class="h-8 w-8 rounded bg-blue-500 flex items-center justify-center mr-2">
                        <i class="fas fa-box text-white text-xs"></i>
                    </div>
                    <div>
                        <div class="font-medium text-gray-900">${productName}</div>
                        <div class="text-gray-500">${title}</div>
                    </div>
                </div>
            </td>
            <td class="px-2 py-3 text-xs border text-center">
                <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded">${category}</span>
            </td>
            <td class="px-2 py-3 text-xs border text-center font-medium">${price}</td>
            <td class="px-2 py-3 text-xs border text-center">
                <span class="px-2 py-1 rounded ${getStatusBadge(status)}">${getStatusIcon(status)}</span>
            </td>
            <td class="px-2 py-3 text-xs border text-center text-gray-500">
                ${formatDateCompact(listing.created_at)}
            </td>
            <td class="px-2 py-3 text-xs border bg-yellow-50">
                <div class="flex space-x-1 justify-center">
                    <button onclick="viewListing('${listingId}')" 
                            class="bg-blue-500 hover:bg-blue-700 text-white p-1 rounded"
                            title="Ver detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="deleteListing('${listingId}')" 
                            class="bg-red-500 hover:bg-red-700 text-white p-1 rounded"
                            title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `;
}

// Generate listing card for mobile view
function generateListingCard(listing) {
    const listingId = listing.id || 'unknown';
    const productName = escapeHtml(listing.product_name || 'Sin nombre');
    const title = escapeHtml(listing.title || 'Sin título');
    const category = escapeHtml(listing.category || 'Sin categoría');
    const price = listing.price ? `$${parseFloat(listing.price).toFixed(0)}` : 'N/A';
    const confidence = listing.confidence_score || 0;
    const status = listing.status || 'draft';
    
    return `
        <div class="border-b border-gray-200 p-4 hover:bg-gray-50">
            <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                    <div class="flex items-center mb-2">
                        <div class="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mr-3">
                            <i class="fas fa-box text-white text-sm"></i>
                        </div>
                        <div class="flex-1 min-w-0">
                            <h4 class="text-sm font-medium text-gray-900 truncate">${productName}</h4>
                            <p class="text-xs text-gray-500 truncate">${title}</p>
                        </div>
                    </div>
                    
                    <div class="flex flex-wrap items-center gap-2 mb-3">
                        <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                            ${category}
                        </span>
                        <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getStatusBadge(status)}">
                            ${getStatusIcon(status)}
                        </span>
                        <span class="text-xs text-gray-900 font-medium">${price}</span>
                    </div>
                    
                    <div class="flex items-center mb-3">
                        <span class="text-xs text-gray-500 mr-2">Confianza:</span>
                        <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                            <div class="h-2 rounded-full ${getConfidenceColor(confidence)}" 
                                 style="width: ${confidence}%"></div>
                        </div>
                        <span class="text-xs text-gray-600">${confidence}%</span>
                    </div>
                    
                    <div class="text-xs text-gray-500 mb-3">
                        Creado: ${formatDateCompact(listing.created_at)}
                    </div>
                </div>
            </div>
            
            <div class="flex justify-end space-x-2">
                <button onclick="viewListing('${listingId}')" 
                        class="px-3 py-1 text-blue-600 hover:text-blue-900 hover:bg-blue-50 rounded text-xs transition-colors"
                        title="Ver detalles">
                    <i class="fas fa-eye mr-1"></i>Ver
                </button>
                <button onclick="deleteListing('${listingId}')" 
                        class="px-3 py-1 text-red-600 hover:text-red-900 hover:bg-red-50 rounded text-xs transition-colors"
                        title="Eliminar">
                    <i class="fas fa-trash mr-1"></i>Eliminar
                </button>
            </div>
        </div>
    `;
}

// Filter listings based on search and filters
function filterListings() {
    console.log('🔍 filterListings called');
    
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    const categoryValue = categoryFilter ? categoryFilter.value : '';
    const statusValue = statusFilter ? statusFilter.value : '';
    
    console.log('Filter values:', { searchTerm, categoryValue, statusValue });
    console.log('Total listings before filter:', allListings.length);
    
    // Log some sample listings for debugging
    if (allListings.length > 0) {
        console.log('Sample listing data:', {
            first: allListings[0],
            categories: [...new Set(allListings.map(l => l.category))],
            statuses: [...new Set(allListings.map(l => l.status))]
        });
    }
    
    filteredListings = allListings.filter(listing => {
        const matchesSearch = !searchTerm || 
            listing.product_name?.toLowerCase().includes(searchTerm) ||
            listing.title?.toLowerCase().includes(searchTerm) ||
            listing.description?.toLowerCase().includes(searchTerm);
        
        const matchesCategory = !categoryValue || listing.category === categoryValue;
        const matchesStatus = !statusValue || listing.status === statusValue;
        
        // Log individual matches for debugging
        if (searchTerm || categoryValue || statusValue) {
            console.log(`Listing ${listing.id}: search=${matchesSearch}, category=${matchesCategory}, status=${matchesStatus}`);
        }
        
        return matchesSearch && matchesCategory && matchesStatus;
    });
    
    console.log('Filtered listings count:', filteredListings.length);
    
    renderListings();
}

// Action functions
function viewListing(listingId) {
    console.log('👁️ View listing:', listingId);
    window.location.href = `listing-details.html?id=${listingId}`;
}

async function deleteListing(listingId) {
    console.log('🗑️ Delete listing:', listingId);
    
    if (!confirm('¿Estás seguro de que quieres eliminar este listing? Esta acción no se puede deshacer.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/listings/${listingId}`, {
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

// Populate filter options dynamically
function populateFilterOptions() {
    console.log('🔄 Populating filter options...');
    
    const categoryFilter = document.getElementById('categoryFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    if (allListings.length > 0) {
        // Get unique categories from actual data
        const uniqueCategories = [...new Set(allListings.map(l => l.category))].filter(c => c && c !== 'Sin categoría');
        const uniqueStatuses = [...new Set(allListings.map(l => l.status))].filter(s => s);
        
        console.log('📊 Unique categories from data:', uniqueCategories);
        console.log('📊 Unique statuses from data:', uniqueStatuses);
        
        // Update category filter
        if (categoryFilter) {
            // Keep the "All categories" option
            const allCategoriesOption = categoryFilter.querySelector('option[value=""]');
            categoryFilter.innerHTML = '';
            categoryFilter.appendChild(allCategoriesOption);
            
            // Add actual categories
            uniqueCategories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                categoryFilter.appendChild(option);
            });
        }
        
        // Update status filter
        if (statusFilter) {
            // Keep the "All statuses" option
            const allStatusesOption = statusFilter.querySelector('option[value=""]');
            statusFilter.innerHTML = '';
            statusFilter.appendChild(allStatusesOption);
            
            // Add actual statuses with Spanish labels
            const statusLabels = {
                'draft': 'Borrador',
                'published': 'Publicado',
                'archived': 'Archivado'
            };
            
            uniqueStatuses.forEach(status => {
                const option = document.createElement('option');
                option.value = status;
                option.textContent = statusLabels[status] || status;
                statusFilter.appendChild(option);
            });
        }
    }
}

// Format category name from backend to display format
function formatCategoryName(category) {
    const categoryMap = {
        'ELECTRONICS': 'Electronics',
        'SPORTS': 'Sports & Outdoors',
        'HOME_GARDEN': 'Home & Garden',
        'HEALTH': 'Health & Personal Care',
        'CLOTHING': 'Clothing, Shoes & Jewelry',
        'AUTOMOTIVE': 'Automotive',
        'TOYS': 'Toys & Games',
        'BOOKS': 'Books'
    };
    
    return categoryMap[category] || category;
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
        console.error('Error formatting date:', error);
        return 'Fecha inválida';
    }
}

// Additional utility functions for better UI
function getStatusIcon(status) {
    switch(status) {
        case 'published': return '✓';
        case 'draft': return '⏳';
        case 'archived': return '📁';
        default: return '⏳';
    }
}

function formatDateCompact(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (error) {
        console.error('Error formatting date:', error);
        return 'N/A';
    }
}
