// Dashboard JavaScript - Updated 2025-07-14
// API Base URL - Configuración dinámica
const API_BASE_URL = (() => {
    // La API siempre está en el puerto 8000
    const apiPort = '8000';
    const currentHost = window.location.hostname || 'localhost';
    const currentProtocol = window.location.protocol || 'http:';
    return `${currentProtocol}//${currentHost}:${apiPort}`;
})();

console.log('API Base URL configurada dinámicamente:', API_BASE_URL);

// Global variables
let allListings = [];
let systemStatus = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loading...');
    
    // Load data in sequence
    checkSystemStatus();
    loadDashboardData();
    
    // Setup refresh interval (every 30 seconds)
    setInterval(refreshData, 30000);
});

// Check system status
async function checkSystemStatus() {
    const statusIndicator = document.getElementById('statusIndicator');
    const systemStatusText = document.getElementById('systemStatus');
    
    try {
        const response = await fetch(`${API_BASE_URL}/status`);
        
        if (response.ok) {
            const status = await response.json();
            systemStatus = status;
            
            statusIndicator.className = 'w-3 h-3 rounded-full bg-green-400 mr-2';
            systemStatusText.textContent = 'Sistema Operativo';
            
            // Update detailed status
            updateDetailedStatus(status);
            
        } else {
            throw new Error('Status check failed');
        }
    } catch (error) {
        console.error('Error checking system status:', error);
        statusIndicator.className = 'w-3 h-3 rounded-full bg-red-400 mr-2';
        systemStatusText.textContent = 'Sistema Desconectado';
        
        // Update with error status
        updateDetailedStatus({ system: 'offline', error: error.message });
    }
}

// Update detailed status in sidebar
function updateDetailedStatus(status) {
    const backendStatus = document.getElementById('backendStatus');
    const aiStatus = document.getElementById('aiStatus');
    const dbStatus = document.getElementById('dbStatus');
    const lastSync = document.getElementById('lastSync');
    
    // Backend status
    if (status.system === 'online') {
        backendStatus.className = 'px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full';
        backendStatus.textContent = 'Conectado';
    } else {
        backendStatus.className = 'px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full';
        backendStatus.textContent = 'Desconectado';
    }
    
    // AI status
    if (status.ollama_connected) {
        aiStatus.className = 'px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full';
        aiStatus.textContent = `Activo (${status.agents_ready}/${status.agents_total})`;
    } else {
        aiStatus.className = 'px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full';
        aiStatus.textContent = 'Limitado';
    }
    
    // DB status (assume working if backend is online)
    if (status.system === 'online') {
        dbStatus.className = 'px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full';
        dbStatus.textContent = 'Conectada';
    } else {
        dbStatus.className = 'px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full';
        dbStatus.textContent = 'Error';
    }
    
    // Last sync
    lastSync.textContent = new Date().toLocaleTimeString('es-ES');
}

// Load main dashboard data
async function loadDashboardData() {
    try {
        // Load listings and metrics in parallel
        const [listingsResponse, metricsResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/api/listings/`),
            fetch(`${API_BASE_URL}/api/listings/metrics`)
        ]);
        
        if (!listingsResponse.ok || !metricsResponse.ok) {
            throw new Error('Failed to load dashboard data');
        }
        
        const listingsData = await listingsResponse.json();
        const metricsData = await metricsResponse.json();
        
        allListings = listingsData.listings || [];
        
        console.log('Dashboard data loaded:', allListings.length, 'listings');
        console.log('Metrics loaded:', metricsData);
        
        // Update dashboard with enhanced metrics
        updateDashboardMetrics(metricsData);
        
        // Update all dashboard components
        updateStats();
        renderRecentListings();
        renderCharts();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Error cargando datos del dashboard', 'error');
        
        // Show empty state
        document.getElementById('recentListings').innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-exclamation-triangle text-4xl text-gray-400 mb-4"></i>
                <h3 class="text-lg font-medium text-gray-900 mb-2">Error cargando datos</h3>
                <p class="text-gray-600 mb-4">No se pudieron cargar los listings</p>
                <button onclick="loadDashboardData()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    Reintentar
                </button>
            </div>
        `;
    }
}

// Update dashboard metrics with real data
function updateDashboardMetrics(metrics) {
    // Update metric cards
    const elements = {
        'totalListings': metrics.total_listings,
        'draftListings': metrics.draft_listings,
        'publishedListings': metrics.published_listings,
        'averageConfidence': `${Math.round(metrics.average_confidence * 100)}%`,
        'systemHealth': metrics.system_health,
        'successRate': `${Math.round(metrics.success_rate * 100)}%`,
        'totalAgentResults': metrics.total_agent_results
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            console.log(`Updated ${id} to:`, value);
        }
    });
    
    // Update health indicator
    const healthElement = document.getElementById('systemHealth');
    if (healthElement) {
        healthElement.className = `px-3 py-1 rounded-full text-sm font-medium ${
            metrics.system_health === 'healthy' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-yellow-100 text-yellow-800'
        }`;
    }
    
    // Update last updated time
    const lastUpdated = document.getElementById('lastUpdated');
    if (lastUpdated) {
        lastUpdated.textContent = new Date(metrics.generated_at).toLocaleString('es-ES');
    }
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
    
    // Update DOM
    document.getElementById('totalListings').textContent = totalListings;
    document.getElementById('publishedListings').textContent = publishedListings;
    document.getElementById('draftListings').textContent = draftListings;
    document.getElementById('avgConfidence').textContent = `${avgConfidence}%`;
}

// Render recent listings
function renderRecentListings() {
    const container = document.getElementById('recentListings');
    
    if (allListings.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-inbox text-4xl text-gray-400 mb-4"></i>
                <h3 class="text-lg font-medium text-gray-900 mb-2">No hay listings</h3>
                <p class="text-gray-600 mb-4">¡Crea tu primer listing para comenzar!</p>
                <a href="create-listing.html" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    Crear Primer Listing
                </a>
            </div>
        `;
        return;
    }
    
    // Show most recent 5 listings
    const recentListings = allListings
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5);
    
    container.innerHTML = `
        <div class="space-y-4">
            ${recentListings.map(listing => `
                <div class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                    <div class="flex-shrink-0 h-12 w-12">
                        <div class="h-12 w-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                            <i class="fas fa-box text-white"></i>
                        </div>
                    </div>
                    <div class="ml-4 flex-1">
                        <h4 class="text-sm font-medium text-gray-900">${listing.product_name || 'Sin nombre'}</h4>
                        <p class="text-sm text-gray-500">${(listing.category || 'Sin categoría').replace('ProductCategory.', '')}</p>
                        <div class="flex items-center mt-1">
                            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getStatusBadge(listing.status)}">
                                ${getStatusText(listing.status)}
                            </span>
                            <span class="ml-2 text-xs text-gray-500">
                                ${formatRelativeTime(listing.created_at)}
                            </span>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <div class="text-right">
                            <p class="text-sm font-medium text-gray-900">$${listing.target_price || 'N/A'}</p>
                            <p class="text-xs text-gray-500">${listing.confidence_score || 0}% confianza</p>
                        </div>
                        <button data-listing-id="${listing.id}" class="view-listing-btn text-blue-600 hover:text-blue-800 p-1" title="Ver detalles">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
        
        ${allListings.length > 5 ? `
            <div class="mt-4 text-center">
                <a href="listings.html" class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                    Ver ${allListings.length - 5} listings más →
                </a>
            </div>
        ` : ''}
    `;
    
    // Add event listeners to view listing buttons
    setTimeout(() => {
        document.querySelectorAll('.view-listing-btn').forEach(button => {
            button.addEventListener('click', function() {
                const listingId = this.getAttribute('data-listing-id');
                console.log('View listing button clicked for ID:', listingId);
                viewListing(listingId);
            });
        });
    }, 100);
}

// Render charts
function renderCharts() {
    renderCategoriesChart();
    renderPerformanceChart();
}

// Categories distribution chart
function renderCategoriesChart() {
    const ctx = document.getElementById('categoriesChart');
    if (!ctx) return;
    
    // Count categories
    const categoryCounts = {};
    allListings.forEach(listing => {
        const category = (listing.category || 'Sin categoría').replace('ProductCategory.', '');
        categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    });
    
    const labels = Object.keys(categoryCounts);
    const data = Object.values(categoryCounts);
    const colors = [
        '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
        '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6B7280'
    ];
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

// Performance chart (confidence scores over time)
function renderPerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    // Group by date and calculate average confidence
    const dailyData = {};
    allListings.forEach(listing => {
        const date = new Date(listing.created_at).toDateString();
        if (!dailyData[date]) {
            dailyData[date] = { total: 0, count: 0 };
        }
        dailyData[date].total += listing.confidence_score || 0;
        dailyData[date].count += 1;
    });
    
    const labels = Object.keys(dailyData).sort();
    const confidenceData = labels.map(date => {
        const day = dailyData[date];
        return day.count > 0 ? Math.round(day.total / day.count) : 0;
    });
    const countData = labels.map(date => dailyData[date].count);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.map(date => new Date(date).toLocaleDateString('es-ES', { 
                month: 'short', 
                day: 'numeric' 
            })),
            datasets: [
                {
                    label: 'Confianza Promedio (%)',
                    data: confidenceData,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'Listings Creados',
                    data: countData,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: false,
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Confianza (%)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Cantidad'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

// Utility functions
function getStatusBadge(status) {
    switch (status) {
        case 'published':
            return 'bg-green-100 text-green-800';
        case 'draft':
            return 'bg-yellow-100 text-yellow-800';
        case 'archived':
            return 'bg-gray-100 text-gray-800';
        default:
            return 'bg-blue-100 text-blue-800';
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

function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffDays > 0) {
        return `Hace ${diffDays} día${diffDays === 1 ? '' : 's'}`;
    } else if (diffHours > 0) {
        return `Hace ${diffHours} hora${diffHours === 1 ? '' : 's'}`;
    } else {
        return 'Hace unos minutos';
    }
}

// Action functions
function viewListing(listingId) {
    console.log('viewListing called with ID:', listingId);
    try {
        window.location.href = `/listing-details.html?id=${listingId}`;
    } catch (error) {
        console.error('Error navigating to listing details:', error);
        alert('Error al navegar a los detalles del listing');
    }
}

function refreshData() {
    console.log('Refreshing dashboard data...');
    checkSystemStatus();
    loadDashboardData();
}

function loadQuickTour() {
    document.getElementById('tourModal').classList.remove('hidden');
}

function closeTour() {
    document.getElementById('tourModal').classList.add('hidden');
}

function openBulkImport() {
    showToast('Función de importación en desarrollo', 'info');
}

function exportListings() {
    if (allListings.length === 0) {
        showToast('No hay listings para exportar', 'warning');
        return;
    }
    
    // Simple CSV export
    const csvContent = "data:text/csv;charset=utf-8," 
        + "ID,Producto,Título,Categoría,Precio,Confianza,Estado,Fecha\n"
        + allListings.map(listing => [
            listing.id,
            `"${listing.product_name || ''}"`,
            `"${listing.title || ''}"`,
            `"${(listing.category || '').replace('ProductCategory.', '')}"`,
            listing.target_price || '',
            listing.confidence_score || '',
            listing.status || '',
            new Date(listing.created_at).toLocaleDateString()
        ].join(",")).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `listings_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showToast('Listings exportados exitosamente', 'success');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    // Remove existing classes
    toast.className = 'fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300';
    
    // Add type-specific styling
    switch (type) {
        case 'success':
            toast.classList.add('bg-green-500', 'text-white');
            break;
        case 'error':
            toast.classList.add('bg-red-500', 'text-white');
            break;
        case 'warning':
            toast.classList.add('bg-yellow-500', 'text-white');
            break;
        default:
            toast.classList.add('bg-blue-500', 'text-white');
    }
    
    toastMessage.textContent = message;
    toast.classList.remove('hidden', 'translate-y-full');
    
    // Auto hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('translate-y-full');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 300);
    }, 3000);
}
