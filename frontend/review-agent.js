/**
 * Servicio para interactuar con el agente revisor
 */

// Configuración base
const API_BASE_URL = getApiBaseUrl();

/**
 * Función para revisar un listing completo
 * @param {Object} reviewData - Datos del producto y agentes para revisar
 * @returns {Promise<Object>} - Resultado de la revisión
 */
async function reviewListing(reviewData) {
    try {
        showLoading('Revisando listing...');
        
        const response = await fetch(`${API_BASE_URL}/listings/review-listing`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(reviewData)
        });

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        hideLoading();
        
        return result;
    } catch (error) {
        hideLoading();
        console.error('Error en revisión de listing:', error);
        throw error;
    }
}

/**
 * Función para realizar una revisión integral desde cero
 * @param {Object} productInput - Datos del producto para revisar
 * @returns {Promise<Object>} - Resultado de la revisión integral
 */
async function comprehensiveReview(productInput) {
    try {
        showLoading('Realizando revisión integral...');
        
        const response = await fetch(`${API_BASE_URL}/listings/comprehensive-review`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(productInput)
        });

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        hideLoading();
        
        return result;
    } catch (error) {
        hideLoading();
        console.error('Error en revisión integral:', error);
        throw error;
    }
}

/**
 * Función para mostrar los resultados de la revisión en la interfaz
 * @param {Object} reviewResult - Resultado de la revisión
 * @param {string} containerId - ID del contenedor donde mostrar los resultados
 */
function displayReviewResults(reviewResult, containerId = 'review-results') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const reviewData = reviewResult.reviewed_listing || reviewResult.data;
    const finalListing = reviewData.final_listing || {};
    const improvements = reviewData.improvements_summary || {};
    const qualityMetrics = reviewData.quality_metrics || {};
    const finalRecommendations = reviewData.final_recommendations || [];
    const imageRecommendations = reviewData.image_recommendations || {};

    container.innerHTML = `
        <div class="review-results-container">
            <div class="review-header">
                <h2>📋 Resultados de la Revisión</h2>
                <div class="review-metadata">
                    <span class="confidence-score">Confianza: ${(reviewResult.confidence * 100).toFixed(1)}%</span>
                    <span class="processing-time">Tiempo: ${reviewResult.processing_time?.toFixed(2)}s</span>
                </div>
            </div>

            <div class="review-tabs">
                <button class="tab-button active" onclick="showReviewTab(event, 'final-listing')">Listing Final</button>
                <button class="tab-button" onclick="showReviewTab(event, 'improvements')">Mejoras</button>
                <button class="tab-button" onclick="showReviewTab(event, 'quality-metrics')">Métricas</button>
                <button class="tab-button" onclick="showReviewTab(event, 'recommendations')">Recomendaciones</button>
                <button class="tab-button" onclick="showReviewTab(event, 'images')">Imágenes</button>
            </div>

            <div id="final-listing" class="tab-content active">
                <div class="listing-section">
                    <h3>📝 Título Optimizado</h3>
                    <div class="optimized-title">${finalListing.title || 'N/A'}</div>
                </div>

                <div class="listing-section">
                    <h3>📄 Descripción Optimizada</h3>
                    <div class="optimized-description">${finalListing.description || 'N/A'}</div>
                </div>

                <div class="listing-section">
                    <h3>🎯 Bullet Points Optimizados</h3>
                    <ul class="optimized-bullets">
                        ${(finalListing.bullet_points || []).map(bullet => `<li>${bullet}</li>`).join('')}
                    </ul>
                </div>

                <div class="listing-section">
                    <h3>🏷️ Categoría y Keywords</h3>
                    <div class="category-keywords">
                        <p><strong>Categoría:</strong> ${finalListing.category || 'N/A'}</p>
                        <p><strong>Keywords:</strong> ${(finalListing.keywords || []).join(', ') || 'N/A'}</p>
                        <p><strong>Keywords Backend:</strong> ${(finalListing.backend_keywords || []).join(', ') || 'N/A'}</p>
                    </div>
                </div>
            </div>

            <div id="improvements" class="tab-content">
                <div class="improvements-section">
                    <h3>📈 Resumen de Mejoras</h3>
                    <div class="improvement-score">
                        <span class="score-label">Puntuación General:</span>
                        <span class="score-value">${improvements.overall_improvement_score?.toFixed(1) || '0.0'}/10</span>
                    </div>
                    
                    <div class="improvement-details">
                        <div class="improvement-item">
                            <h4>🎯 Mejoras en Título</h4>
                            <ul>${(improvements.title_improvements || []).map(item => `<li>${item}</li>`).join('')}</ul>
                        </div>
                        <div class="improvement-item">
                            <h4>📝 Mejoras en Descripción</h4>
                            <ul>${(improvements.description_improvements || []).map(item => `<li>${item}</li>`).join('')}</ul>
                        </div>
                        <div class="improvement-item">
                            <h4>🎯 Mejoras en Bullets</h4>
                            <ul>${(improvements.bullet_improvements || []).map(item => `<li>${item}</li>`).join('')}</ul>
                        </div>
                    </div>
                </div>
            </div>

            <div id="quality-metrics" class="tab-content">
                <div class="quality-section">
                    <h3>🏆 Métricas de Calidad</h3>
                    <div class="quality-grid">
                        <div class="quality-metric">
                            <span class="metric-label">Título</span>
                            <div class="metric-bar">
                                <div class="metric-fill" style="width: ${(qualityMetrics.title_quality * 100) || 0}%"></div>
                            </div>
                            <span class="metric-value">${((qualityMetrics.title_quality || 0) * 100).toFixed(1)}%</span>
                        </div>
                        <div class="quality-metric">
                            <span class="metric-label">Descripción</span>
                            <div class="metric-bar">
                                <div class="metric-fill" style="width: ${(qualityMetrics.description_quality * 100) || 0}%"></div>
                            </div>
                            <span class="metric-value">${((qualityMetrics.description_quality || 0) * 100).toFixed(1)}%</span>
                        </div>
                        <div class="quality-metric">
                            <span class="metric-label">Bullet Points</span>
                            <div class="metric-bar">
                                <div class="metric-fill" style="width: ${(qualityMetrics.bullet_quality * 100) || 0}%"></div>
                            </div>
                            <span class="metric-value">${((qualityMetrics.bullet_quality || 0) * 100).toFixed(1)}%</span>
                        </div>
                        <div class="quality-metric">
                            <span class="metric-label">Categoría</span>
                            <div class="metric-bar">
                                <div class="metric-fill" style="width: ${(qualityMetrics.category_accuracy * 100) || 0}%"></div>
                            </div>
                            <span class="metric-value">${((qualityMetrics.category_accuracy || 0) * 100).toFixed(1)}%</span>
                        </div>
                        <div class="quality-metric">
                            <span class="metric-label">Keywords</span>
                            <div class="metric-bar">
                                <div class="metric-fill" style="width: ${(qualityMetrics.keyword_relevance * 100) || 0}%"></div>
                            </div>
                            <span class="metric-value">${((qualityMetrics.keyword_relevance || 0) * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
            </div>

            <div id="recommendations" class="tab-content">
                <div class="recommendations-section">
                    <h3>💡 Recomendaciones Finales</h3>
                    <div class="recommendations-list">
                        ${finalRecommendations.map((rec, index) => `
                            <div class="recommendation-item">
                                <span class="recommendation-number">${index + 1}</span>
                                <span class="recommendation-text">${rec}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>

            <div id="images" class="tab-content">
                <div class="images-section">
                    <h3>📸 Recomendaciones de Imágenes</h3>
                    <div class="image-stats">
                        <p><strong>Imágenes encontradas:</strong> ${imageRecommendations.optimized_images?.length || 0}</p>
                        <p><strong>Confianza:</strong> ${((imageRecommendations.image_confidence || 0) * 100).toFixed(1)}%</p>
                        <p><strong>Términos de búsqueda:</strong> ${(imageRecommendations.image_search_terms || []).join(', ') || 'N/A'}</p>
                    </div>
                    <div class="image-grid">
                        ${(imageRecommendations.optimized_images || []).map(img => `
                            <div class="image-item">
                                <img src="${img.url}" alt="${img.description || 'Imagen del producto'}" loading="lazy">
                                <div class="image-info">
                                    <p class="image-description">${img.description || 'N/A'}</p>
                                    <p class="image-relevance">Relevancia: ${((img.relevance_score || 0) * 100).toFixed(1)}%</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;

    // Agregar estilos CSS si no existen
    if (!document.getElementById('review-styles')) {
        const style = document.createElement('style');
        style.id = 'review-styles';
        style.textContent = `
            .review-results-container {
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin: 20px 0;
            }
            
            .review-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #f0f0f0;
            }
            
            .review-metadata {
                display: flex;
                gap: 15px;
            }
            
            .confidence-score, .processing-time {
                background: #e8f4f8;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 0.9em;
                font-weight: 500;
            }
            
            .review-tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                border-bottom: 1px solid #ddd;
            }
            
            .tab-button {
                background: none;
                border: none;
                padding: 10px 20px;
                cursor: pointer;
                font-weight: 500;
                color: #666;
                border-bottom: 2px solid transparent;
                transition: all 0.3s;
            }
            
            .tab-button.active {
                color: #007cba;
                border-bottom-color: #007cba;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .listing-section {
                margin-bottom: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
            }
            
            .optimized-title {
                font-size: 1.2em;
                font-weight: 600;
                color: #2c3e50;
                padding: 10px;
                background: white;
                border-radius: 5px;
                border-left: 4px solid #007cba;
            }
            
            .optimized-description {
                white-space: pre-wrap;
                line-height: 1.6;
                padding: 10px;
                background: white;
                border-radius: 5px;
            }
            
            .optimized-bullets {
                list-style: none;
                padding: 0;
            }
            
            .optimized-bullets li {
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }
            
            .improvement-score {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 15px;
            }
            
            .score-value {
                font-size: 1.5em;
                font-weight: bold;
                color: #007cba;
            }
            
            .improvement-details {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px;
            }
            
            .improvement-item {
                background: white;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #28a745;
            }
            
            .quality-grid {
                display: grid;
                gap: 15px;
            }
            
            .quality-metric {
                display: flex;
                align-items: center;
                gap: 15px;
                padding: 10px;
                background: white;
                border-radius: 8px;
            }
            
            .metric-label {
                min-width: 100px;
                font-weight: 500;
            }
            
            .metric-bar {
                flex: 1;
                height: 20px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
            }
            
            .metric-fill {
                height: 100%;
                background: linear-gradient(90deg, #28a745, #20c997);
                transition: width 0.3s ease;
            }
            
            .metric-value {
                min-width: 50px;
                text-align: right;
                font-weight: 500;
            }
            
            .recommendations-list {
                display: grid;
                gap: 10px;
            }
            
            .recommendation-item {
                display: flex;
                gap: 15px;
                padding: 12px;
                background: white;
                border-radius: 8px;
                border-left: 4px solid #ffc107;
            }
            
            .recommendation-number {
                background: #ffc107;
                color: white;
                width: 25px;
                height: 25px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 0.9em;
            }
            
            .image-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            
            .image-item {
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            .image-item img {
                width: 100%;
                height: 150px;
                object-fit: cover;
            }
            
            .image-info {
                padding: 10px;
                font-size: 0.9em;
            }
            
            .image-description {
                margin-bottom: 5px;
                color: #666;
            }
            
            .image-relevance {
                font-weight: 500;
                color: #007cba;
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Función para cambiar entre tabs de resultados
 */
function showReviewTab(event, tabName) {
    // Ocultar todos los contenidos
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));
    
    // Desactivar todos los botones
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));
    
    // Mostrar el contenido seleccionado
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

/**
 * Función para crear un botón de revisión en el formulario
 */
function addReviewButton(formId, buttonText = 'Revisar con IA') {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const existingButton = form.querySelector('.review-button');
    if (existingButton) return; // Ya existe
    
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'review-button btn btn-secondary';
    button.textContent = buttonText;
    button.style.marginLeft = '10px';
    
    button.addEventListener('click', async () => {
        try {
            // Obtener datos del formulario
            const formData = new FormData(form);
            const productData = Object.fromEntries(formData);
            
            // Ejecutar revisión integral
            const result = await comprehensiveReview(productData);
            
            if (result.success) {
                displayReviewResults(result);
                showNotification('Revisión completada exitosamente', 'success');
            } else {
                showNotification('Error en la revisión: ' + result.error, 'error');
            }
        } catch (error) {
            showNotification('Error al revisar: ' + error.message, 'error');
        }
    });
    
    // Agregar el botón al formulario
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.parentNode.insertBefore(button, submitButton.nextSibling);
    } else {
        form.appendChild(button);
    }
}

// Inicializar automáticamente cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Agregar botones de revisión a formularios existentes
    addReviewButton('create-listing-form', '🔍 Revisar con IA');
    addReviewButton('product-form', '🔍 Revisar Producto');
    
    // Crear contenedor para resultados si no existe
    if (!document.getElementById('review-results')) {
        const container = document.createElement('div');
        container.id = 'review-results';
        container.style.marginTop = '20px';
        
        const mainContent = document.querySelector('.main-content, .container, main');
        if (mainContent) {
            mainContent.appendChild(container);
        }
    }
});

// Exportar funciones para uso global
window.reviewListing = reviewListing;
window.comprehensiveReview = comprehensiveReview;
window.displayReviewResults = displayReviewResults;
window.showReviewTab = showReviewTab;
window.addReviewButton = addReviewButton;
