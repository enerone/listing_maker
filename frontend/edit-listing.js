// Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global variables
let currentListing = null;
let listingId = null;
let bulletPointCount = 0;

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Edit listing page loaded');
    
    // Get listing ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    listingId = urlParams.get('id');
    
    if (!listingId) {
        showError('No se especificó un ID de listing válido');
        return;
    }
    
    // Check system status
    checkSystemStatus();
    
    // Load listing data
    loadListing();
    
    // Setup form handler
    setupFormHandler();
});

// Check system status
async function checkSystemStatus() {
    const statusIndicator = document.getElementById('statusIndicator');
    const systemStatus = document.getElementById('systemStatus');
    
    try {
        const response = await fetch(`${API_BASE_URL}/status`);
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

// Load listing data
async function loadListing() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/listings/${listingId}`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        currentListing = data.listing;
        
        console.log('Loaded listing:', currentListing);
        
        // Populate form with current data
        populateForm(currentListing);
        
        // Show edit form
        document.getElementById('loadingState').classList.add('hidden');
        document.getElementById('editForm').classList.remove('hidden');
        
    } catch (error) {
        console.error('Error loading listing:', error);
        showError(`Error al cargar el listing: ${error.message}`);
    }
}

// Populate form with listing data
function populateForm(listing) {
    // Basic information
    document.getElementById('title').value = listing.title || '';
    document.getElementById('category').value = listing.category || '';
    document.getElementById('price').value = listing.target_price || listing.price || '';
    document.getElementById('description').value = listing.description || '';
    
    // Keywords
    if (listing.search_terms && Array.isArray(listing.search_terms)) {
        document.getElementById('searchTerms').value = listing.search_terms.join(', ');
    }
    
    if (listing.backend_keywords && Array.isArray(listing.backend_keywords)) {
        document.getElementById('backendKeywords').value = listing.backend_keywords.join(', ');
    }
    
    // Bullet points
    const bulletPointsContainer = document.getElementById('bulletPointsContainer');
    bulletPointsContainer.innerHTML = '';
    bulletPointCount = 0;
    
    if (listing.bullet_points && Array.isArray(listing.bullet_points)) {
        listing.bullet_points.forEach(point => {
            addBulletPoint(point);
        });
    }
    
    // Add at least one bullet point if none exist
    if (bulletPointCount === 0) {
        addBulletPoint();
    }
}

// Add bullet point input
function addBulletPoint(value = '') {
    const container = document.getElementById('bulletPointsContainer');
    const div = document.createElement('div');
    div.className = 'flex items-center space-x-3';
    
    div.innerHTML = `
        <div class="flex-1">
            <input type="text" 
                   name="bulletPoint_${bulletPointCount}" 
                   value="${escapeHtml(value)}"
                   placeholder="Punto clave del producto..."
                   class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
        </div>
        <button type="button" onclick="removeBulletPoint(this)" 
                class="text-red-600 hover:text-red-800 p-2">
            <i class="fas fa-trash"></i>
        </button>
    `;
    
    container.appendChild(div);
    bulletPointCount++;
}

// Remove bullet point
function removeBulletPoint(button) {
    const container = document.getElementById('bulletPointsContainer');
    if (container.children.length > 1) {
        button.parentElement.remove();
    } else {
        showToast('Debe mantener al menos un punto clave', 'warning');
    }
}

// Setup form handler
function setupFormHandler() {
    const form = document.getElementById('listingForm');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        await saveListing();
    });
}

// Save listing
async function saveListing() {
    try {
        // Collect form data
        const formData = collectFormData();
        
        console.log('Saving listing with data:', formData);
        
        // Show loading state
        const submitButton = document.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Guardando...';
        submitButton.disabled = true;
        
        // Send update request
        const response = await fetch(`${API_BASE_URL}/api/listings/${listingId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                updates: formData,
                change_reason: 'Manual edit from frontend'
            })
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        showToast('Listing actualizado exitosamente', 'success');
        
        // Redirect to listings page after short delay
        setTimeout(() => {
            window.location.href = 'listings.html';
        }, 1500);
        
    } catch (error) {
        console.error('Error saving listing:', error);
        showToast(`Error al guardar: ${error.message}`, 'error');
        
        // Restore button state
        const submitButton = document.querySelector('button[type="submit"]');
        submitButton.innerHTML = '<i class="fas fa-save mr-2"></i>Guardar Cambios';
        submitButton.disabled = false;
    }
}

// Collect form data
function collectFormData() {
    const formData = {
        title: document.getElementById('title').value.trim(),
        category: document.getElementById('category').value,
        target_price: parseFloat(document.getElementById('price').value) || null,
        description: document.getElementById('description').value.trim(),
        search_terms: [],
        backend_keywords: [],
        bullet_points: []
    };
    
    // Collect search terms
    const searchTermsText = document.getElementById('searchTerms').value.trim();
    if (searchTermsText) {
        formData.search_terms = searchTermsText.split(',').map(term => term.trim()).filter(term => term);
    }
    
    // Collect backend keywords
    const backendKeywordsText = document.getElementById('backendKeywords').value.trim();
    if (backendKeywordsText) {
        formData.backend_keywords = backendKeywordsText.split(',').map(keyword => keyword.trim()).filter(keyword => keyword);
    }
    
    // Collect bullet points
    const bulletInputs = document.querySelectorAll('input[name^="bulletPoint_"]');
    bulletInputs.forEach(input => {
        const value = input.value.trim();
        if (value) {
            formData.bullet_points.push(value);
        }
    });
    
    return formData;
}

// Preview listing
function previewListing() {
    const formData = collectFormData();
    
    let previewHtml = `
        <div class="space-y-6">
            <div>
                <h4 class="font-semibold text-gray-900 mb-2">Título</h4>
                <p class="text-sm text-gray-700">${escapeHtml(formData.title)}</p>
            </div>
            
            <div>
                <h4 class="font-semibold text-gray-900 mb-2">Categoría</h4>
                <p class="text-sm text-gray-700">${escapeHtml(formData.category)}</p>
            </div>
            
            ${formData.target_price ? `
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">Precio</h4>
                    <p class="text-sm text-gray-700">$${formData.target_price.toFixed(2)}</p>
                </div>
            ` : ''}
            
            <div>
                <h4 class="font-semibold text-gray-900 mb-2">Puntos Clave</h4>
                <ul class="text-sm text-gray-700 space-y-1">
                    ${formData.bullet_points.map(point => 
                        `<li>• ${escapeHtml(point)}</li>`
                    ).join('')}
                </ul>
            </div>
            
            <div>
                <h4 class="font-semibold text-gray-900 mb-2">Descripción</h4>
                <p class="text-sm text-gray-700 whitespace-pre-wrap">${escapeHtml(formData.description)}</p>
            </div>
            
            ${formData.search_terms.length > 0 ? `
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">Términos de Búsqueda</h4>
                    <p class="text-sm text-gray-700">${formData.search_terms.join(', ')}</p>
                </div>
            ` : ''}
            
            ${formData.backend_keywords.length > 0 ? `
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">Keywords Backend</h4>
                    <p class="text-sm text-gray-700">${formData.backend_keywords.join(', ')}</p>
                </div>
            ` : ''}
        </div>
    `;
    
    document.getElementById('previewContent').innerHTML = previewHtml;
    document.getElementById('previewModal').classList.remove('hidden');
}

// Close preview modal
function closePreview() {
    document.getElementById('previewModal').classList.add('hidden');
}

// Cancel edit
function cancelEdit() {
    if (confirm('¿Estás seguro de que quieres cancelar? Los cambios no guardados se perderán.')) {
        window.location.href = 'listings.html';
    }
}

// Show error state
function showError(message) {
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('editForm').classList.add('hidden');
    document.getElementById('errorState').classList.remove('hidden');
    document.getElementById('errorMessage').textContent = message;
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    // Set message
    toastMessage.textContent = message;
    
    // Set style based on type
    toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'warning' ? 'bg-yellow-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    
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

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
