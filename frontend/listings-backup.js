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
    // Search input
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce(filterListings, 300));
    
    // Filter selects
    const categoryFilter = document.getElementById('categoryFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    categoryFilter.addEventListener('change', filterListings);
    statusFilter.addEventListener('change', filterListings);
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
            statusIndicator.className = 'w-3 h-3 rounded-full bg-green-400 mr-2';
            systemStatus.textContent = 'Sistema Operativo';
        } else {
            throw new Error('Health check failed');
        }
    } catch (error) {
        console.error('Error checking system status:', error);
        statusIndicator.className = 'w-3 h-3 rounded-full bg-red-400 mr-2';
        systemStatus.textContent = 'Sistema Desconectado';
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
    
    console.log('Loading element:', loadingEl);
    console.log('Empty element:', emptyEl);
    console.log('Table element:', tableEl);
    
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
    
    document.getElementById('totalListings').textContent = totalListings;
    document.getElementById('publishedListings').textContent = publishedListings;
    document.getElementById('draftListings').textContent = draftListings;
    document.getElementById('avgConfidence').textContent = `${avgConfidence}%`;
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
            // Show table but with "no results" message
            showListingsTable();
            const tbody = document.getElementById('listingsTableBody');
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-8 text-center text-gray-500">
                        <i class="fas fa-search text-2xl mb-2"></i>
                        <p>No se encontraron listings con los filtros aplicados</p>
                    </td>
                </tr>
            `;
        }
        return;
    }
    
    console.log('Showing listings table with', filteredListings.length, 'listings');
    showListingsTable();
    
    const tbody = document.getElementById('listingsTableBody');
    
    // Debug: log the first listing to see its structure
    if (filteredListings.length > 0) {
        console.log('First listing structure:', filteredListings[0]);
    }
    
    tbody.innerHTML = filteredListings.map(listing => {
        console.log('Processing listing:', listing.id || 'no-id', listing.product_name || 'no-name');
        
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
                        <div class="text-sm font-medium text-gray-900">${escapeHtml(listing.product_name || 'Sin nombre')}</div>
                        <div class="text-sm text-gray-500">${escapeHtml(truncateText(listing.title || 'Sin título', 50))}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    ${escapeHtml(listing.category || 'Sin categoría')}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${listing.price ? `$${parseFloat(listing.price).toFixed(2)}` : 'No definido'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                        <div class="h-2 rounded-full ${getConfidenceColor(listing.confidence_score)}" 
                             style="width: ${listing.confidence_score || 0}%"></div>
                    </div>
                    <span class="text-sm text-gray-600">${listing.confidence_score || 0}%</span>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(listing.status)}">
                    ${getStatusText(listing.status)}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatDate(listing.created_at)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                    <button onclick="viewListing('${listing.id}')" 
                            class="text-blue-600 hover:text-blue-900 transition-colors"
                            title="Ver detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button onclick="editListing('${listing.id}')" 
                            class="text-green-600 hover:text-green-900 transition-colors"
                            title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="duplicateListing('${listing.id}')" 
                            class="text-purple-600 hover:text-purple-900 transition-colors"
                            title="Duplicar">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button onclick="deleteListing('${listing.id}')" 
                            class="text-red-600 hover:text-red-900 transition-colors"
                            title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `}).join('');
}

// Filter listings based on search and filters
function filterListings() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    
    filteredListings = allListings.filter(listing => {
        const matchesSearch = !searchTerm || 
            (listing.product_name && listing.product_name.toLowerCase().includes(searchTerm)) ||
            (listing.title && listing.title.toLowerCase().includes(searchTerm)) ||
            (listing.description && listing.description.toLowerCase().includes(searchTerm));
        
        const matchesCategory = !categoryFilter || listing.category === categoryFilter;
        const matchesStatus = !statusFilter || listing.status === statusFilter;
        
        return matchesSearch && matchesCategory && matchesStatus;
    });
    
    renderListings();
}

// View listing details in modal
async function viewListing(listingId) {
    console.log('🔍 ViewListing called with ID:', listingId);
    
    try {
        // First, try to find in local cache
        let listing = allListings.find(l => l.id == listingId);
        
        if (!listing) {
            console.error('❌ Listing not found in cache with ID:', listingId);
            showToast('Listing no encontrado', 'error');
            return;
        }
        
        console.log('✅ Listing found:', listing);
        
        // Get modal elements
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        const modal = document.getElementById('listingModal');
        
        if (!modalTitle || !modalContent || !modal) {
            console.error('❌ Modal elements not found');
            alert(`Ver detalle: ${listing.product_name || listingId}`);
            return;
        }
        
        // Set modal title
        modalTitle.textContent = `Detalles: ${listing.product_name || 'Sin nombre'}`;
        
        // Create modal content with available data
        modalContent.innerHTML = `
            <div class="space-y-6 max-h-96 overflow-y-auto">
                <!-- Basic Info -->
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="font-semibold text-gray-900 mb-3">Información Básica</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Nombre del Producto</label>
                            <p class="text-sm text-gray-900">${escapeHtml(listing.product_name || 'No definido')}</p>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Categoría</label>
                            <p class="text-sm text-gray-900">${escapeHtml(listing.category || 'No definido')}</p>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Precio Objetivo</label>
                            <p class="text-sm text-gray-900">${listing.target_price ? `$${parseFloat(listing.target_price).toFixed(2)}` : 'No definido'}</p>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Confianza</label>
                            <p class="text-sm text-gray-900">${Math.round((listing.confidence_score || 0) * 100)}%</p>
                        </div>
                    </div>
                </div>
                
                <!-- Title -->
                <div>
                    <h4 class="font-semibold text-gray-900 mb-3">Título Generado</h4>
                    <p class="text-sm text-gray-900 bg-gray-50 p-3 rounded-lg">${escapeHtml(listing.title || 'No definido')}</p>
                </div>
                
                <!-- Bullet Points -->
                ${listing.bullet_points && listing.bullet_points.length > 0 ? `
                <div>
                    <h4 class="font-semibold text-gray-900 mb-3">Puntos Clave</h4>
                    <ul class="space-y-2">
                        ${listing.bullet_points.map(point => `
                            <li class="text-sm text-gray-900 bg-gray-50 p-2 rounded-lg flex items-start">
                                <span class="mr-2">•</span>
                                <span>${escapeHtml(point)}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                ` : ''}
                
                <!-- Description -->
                ${listing.description ? `
                <div>
                    <h4 class="font-semibold text-gray-900 mb-3">Descripción</h4>
                    <div class="text-sm text-gray-900 bg-gray-50 p-3 rounded-lg whitespace-pre-wrap">${escapeHtml(listing.description)}</div>
                </div>
                ` : ''}
                
                <!-- Search Terms & Keywords -->
                ${(listing.search_terms && listing.search_terms.length > 0) || (listing.backend_keywords && listing.backend_keywords.length > 0) ? `
                <div class="bg-blue-50 p-4 rounded-lg">
                    <h4 class="font-semibold text-gray-900 mb-3">SEO y Keywords</h4>
                    ${listing.search_terms && listing.search_terms.length > 0 ? `
                        <div class="mb-3">
                            <label class="block text-sm font-medium text-gray-700 mb-1">Términos de Búsqueda</label>
                            <div class="flex flex-wrap gap-1">
                                ${listing.search_terms.map(term => `
                                    <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                                        ${escapeHtml(term)}
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    ${listing.backend_keywords && listing.backend_keywords.length > 0 ? `
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Keywords Backend</label>
                            <div class="flex flex-wrap gap-1">
                                ${listing.backend_keywords.map(keyword => `
                                    <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-100 text-green-800">
                                        ${escapeHtml(keyword)}
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                ` : ''}
                
                <!-- Agent Results Summary -->
                ${data.agent_results && data.agent_results.length > 0 ? `
                <div class="bg-purple-50 p-4 rounded-lg">
                    <h4 class="font-semibold text-gray-900 mb-3">Resultados de Agentes IA</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        ${data.agent_results.map(agent => `
                            <div class="bg-white p-3 rounded-lg border">
                                <div class="flex items-center justify-between mb-2">
                                    <span class="text-sm font-medium text-gray-900">${escapeHtml(agent.agent_name)}</span>
                                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                        agent.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                    }">
                                        ${agent.status}
                                    </span>
                                </div>
                                <div class="text-xs text-gray-600">
                                    <div>Confianza: ${Math.round((agent.confidence || 0) * 100)}%</div>
                                    <div>Tiempo: ${(agent.processing_time || 0).toFixed(1)}s</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                <!-- Competitive Analysis & Social Content -->
                ${getCompetitiveAndSocialContent(data.agent_results)}
                
                <!-- Processing Notes -->
                ${listing.processing_notes && listing.processing_notes.length > 0 ? `
                <div class="bg-green-50 p-4 rounded-lg">
                    <h4 class="font-semibold text-gray-900 mb-3">Notas de Procesamiento</h4>
                    <ul class="space-y-1">
                        ${listing.processing_notes.map(note => `
                            <li class="text-sm text-green-800 flex items-start">
                                <span class="mr-2">✓</span>
                                <span>${escapeHtml(note)}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                ` : ''}
                
                <!-- Recommendations -->
                ${listing.recommendations && listing.recommendations.length > 0 ? `
                <div class="bg-yellow-50 p-4 rounded-lg">
                    <h4 class="font-semibold text-gray-900 mb-3">Recomendaciones</h4>
                    <ul class="space-y-1">
                        ${listing.recommendations.map(rec => `
                            <li class="text-sm text-yellow-800 flex items-start">
                                <span class="mr-2">💡</span>
                                <span>${escapeHtml(rec)}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                ` : ''}
                
                <!-- Metadata -->
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="font-semibold text-gray-900 mb-3">Metadatos</h4>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                            <label class="block font-medium text-gray-700">Estado</label>
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(listing.status)}">
                                ${getStatusText(listing.status)}
                            </span>
                        </div>
                        <div>
                            <label class="block font-medium text-gray-700">Versión</label>
                            <p class="text-gray-900">${listing.version || 1}</p>
                        </div>
                        <div>
                            <label class="block font-medium text-gray-700">Fecha de Creación</label>
                            <p class="text-gray-900">${formatDate(listing.created_at)}</p>
                        </div>
                        <div>
                            <label class="block font-medium text-gray-700">ID en Base de Datos</label>
                            <p class="text-gray-900">${listing.id}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Actions -->
                <div class="flex justify-end space-x-3 pt-4 border-t">
                    <button onclick="closeModal()" class="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg font-medium transition-colors">
                        Cerrar
                    </button>
                    <button onclick="editListing(${listing.id})" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                        Editar
                    </button>
                </div>
            </div>
        `;
        
        // Show modal
        console.log('🚀 Opening modal...');
        modal.classList.remove('hidden');
        console.log('✅ Modal should be visible now');
        
    } catch (error) {
        console.error('❌ Error in viewListing:', error);
        alert(`Error al ver detalle: ${error.message}`);
    }
}

// Close modal
function closeModal() {
    document.getElementById('listingModal').classList.add('hidden');
}

// Edit listing
function editListing(listingId) {
    // Redirect to edit page
    window.location.href = `edit-listing.html?id=${listingId}`;
}

// Delete listing
async function deleteListing(listingId) {
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
        
        const result = await response.json();
        
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

// Duplicate listing
async function duplicateListing(listingId) {
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

// Helper function to get competitive analysis and social content
function getCompetitiveAndSocialContent(agentResults) {
    if (!agentResults || !Array.isArray(agentResults)) return '';
    
    const competitiveAgent = agentResults.find(agent => 
        agent.agent_name && agent.agent_name.toLowerCase().includes('competitive')
    );
    
    const socialAgent = agentResults.find(agent => 
        agent.agent_name && agent.agent_name.toLowerCase().includes('social')
    );
    
    let content = '';
    
    // Competitive Analysis Section
    if (competitiveAgent && competitiveAgent.agent_data && competitiveAgent.status === 'success') {
        const data = competitiveAgent.agent_data;
        content += `
        <div class="bg-orange-50 p-4 rounded-lg">
            <h4 class="font-semibold text-gray-900 mb-3">🏆 Análisis Competitivo</h4>
            
            ${data.competitors && data.competitors.length > 0 ? `
                <div class="mb-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Competidores Principales</label>
                    <div class="space-y-1">
                        ${data.competitors.map(competitor => `
                            <div class="text-sm bg-white p-2 rounded border">
                                ${escapeHtml(competitor)}
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${data.competitive_advantages && data.competitive_advantages.length > 0 ? `
                <div class="mb-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Ventajas Competitivas</label>
                    <div class="space-y-2">
                        ${data.competitive_advantages.map(advantage => `
                            <div class="text-sm bg-white p-2 rounded border">
                                <div class="font-medium">${escapeHtml(advantage.advantage || '')}</div>
                                <div class="text-gray-600 text-xs mt-1">
                                    Fuerza: ${escapeHtml(advantage.strength || 'N/A')} | 
                                    Impacto: ${escapeHtml(advantage.impact || 'N/A')}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${data.market_positioning ? `
                <div class="mb-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Posicionamiento</label>
                    <div class="text-sm bg-white p-2 rounded border">
                        ${escapeHtml(data.market_positioning)}
                    </div>
                </div>
            ` : ''}
        </div>
        `;
    }
    
    // Social Content Section  
    if (socialAgent && socialAgent.agent_data && socialAgent.status === 'success') {
        const data = socialAgent.agent_data;
        content += `
        <div class="bg-pink-50 p-4 rounded-lg">
            <h4 class="font-semibold text-gray-900 mb-3">📱 Contenido Social</h4>
            
            ${data.hashtags ? `
                <div class="mb-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Hashtags Estratégicos</label>
                    <div class="space-y-2">
                        ${data.hashtags.primary && data.hashtags.primary.length > 0 ? `
                            <div>
                                <span class="text-xs font-medium text-gray-600">Principales:</span>
                                <div class="flex flex-wrap gap-1 mt-1">
                                    ${data.hashtags.primary.map(tag => `
                                        <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-pink-100 text-pink-800">
                                            ${escapeHtml(tag)}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${data.hashtags.secondary && data.hashtags.secondary.length > 0 ? `
                            <div>
                                <span class="text-xs font-medium text-gray-600">Secundarios:</span>
                                <div class="flex flex-wrap gap-1 mt-1">
                                    ${data.hashtags.secondary.map(tag => `
                                        <span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-purple-100 text-purple-800">
                                            ${escapeHtml(tag)}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${data.social_content ? `
                <div class="mb-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Contenido para Redes</label>
                    <div class="space-y-2">
                        ${data.social_content.instagram_post ? `
                            <div class="bg-white p-2 rounded border">
                                <div class="text-xs font-medium text-gray-600 mb-1">📸 Instagram:</div>
                                <div class="text-sm">${escapeHtml(data.social_content.instagram_post)}</div>
                            </div>
                        ` : ''}
                        
                        ${data.social_content.facebook_post ? `
                            <div class="bg-white p-2 rounded border">
                                <div class="text-xs font-medium text-gray-600 mb-1">📘 Facebook:</div>
                                <div class="text-sm">${escapeHtml(data.social_content.facebook_post)}</div>
                            </div>
                        ` : ''}
                        
                        ${data.social_content.tiktok_hooks && data.social_content.tiktok_hooks.length > 0 ? `
                            <div class="bg-white p-2 rounded border">
                                <div class="text-xs font-medium text-gray-600 mb-1">🎵 TikTok Hooks:</div>
                                <ul class="text-sm space-y-1">
                                    ${data.social_content.tiktok_hooks.map(hook => `
                                        <li>• ${escapeHtml(hook)}</li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
        </div>
        `;
    }
    
    return content;
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function getConfidenceColor(score) {
    if (!score) return 'bg-gray-300';
    if (score >= 80) return 'bg-green-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
}

function getStatusBadge(status) {
    switch (status) {
        case 'published':
            return 'bg-green-100 text-green-800';
        case 'draft':
            return 'bg-yellow-100 text-yellow-800';
        case 'archived':
            return 'bg-gray-100 text-gray-800';
        default:
            return 'bg-red-100 text-red-800';
    }
}

function getStatusText(status) {
    switch (status) {
        case 'published':
            return 'Publicado';
        case 'draft':
            return 'Borrador';
        case 'archived':
            return 'Archivado';
        default:
            return 'Desconocido';
    }
}

function formatDate(dateString) {
    if (!dateString) return 'No definido';
    
    const options = { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false 
    };
    
    // Replace T with a space and remove timezone info
    const dateStr = dateString.replace('T', ' ').replace(/\..+/, '');
    
    return new Intl.DateTimeFormat('es-ES', options).format(new Date(dateStr));
}
