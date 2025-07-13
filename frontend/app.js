// Estado global de la aplicación
let currentStep = 1;
let formData = {};
let generatedListing = null;

// API Base URL
const API_BASE = 'http://localhost:8000';

// Funciones globales para onclick (deben estar disponibles inmediatamente)
function addFeatureField() {
    console.log('🔧 Ejecutando addFeatureField()...');
    
    const container = document.getElementById('featuresContainer');
    
    if (!container) {
        console.error('❌ Container featuresContainer no encontrado');
        alert('Error: No se pudo encontrar el contenedor de características');
        return;
    }
    
    console.log('✅ Container encontrado:', container);
    
    // Crear div wrapper para el input y botón eliminar
    const wrapper = document.createElement('div');
    wrapper.className = 'flex items-center space-x-2 feature-wrapper';
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'feature-input w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent';
    input.placeholder = 'Ej: Resistente al agua IP68';
    
    // Botón para eliminar
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'text-red-600 hover:text-red-800 px-2 py-1';
    removeBtn.innerHTML = '<i class="fas fa-times"></i>';
    removeBtn.onclick = function() {
        console.log('🗑️ Eliminando característica');
        wrapper.remove();
    };
    
    wrapper.appendChild(input);
    wrapper.appendChild(removeBtn);
    container.appendChild(wrapper);
    
    console.log('✅ Nueva característica agregada');
    
    // Enfocar el nuevo input
    input.focus();
    
    // Agregar animación
    wrapper.style.opacity = '0';
    wrapper.style.transform = 'translateY(-10px)';
    requestAnimationFrame(() => {
        wrapper.style.transition = 'all 0.3s ease';
        wrapper.style.opacity = '1';
        wrapper.style.transform = 'translateY(0)';
    });
}

function addBoxContentField() {
    console.log('🔧 Ejecutando addBoxContentField()...');
    
    const container = document.getElementById('boxContentsContainer');
    
    if (!container) {
        console.error('❌ Container boxContentsContainer no encontrado');
        alert('Error: No se pudo encontrar el contenedor de contenido de caja');
        return;
    }
    
    console.log('✅ Container encontrado:', container);
    
    // Crear div wrapper para el input y botón eliminar
    const wrapper = document.createElement('div');
    wrapper.className = 'flex items-center space-x-2 box-content-wrapper';
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'box-content-input w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent';
    input.placeholder = 'Ej: 1x Cable de carga magnético';
    
    // Botón para eliminar
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'text-red-600 hover:text-red-800 px-2 py-1';
    removeBtn.innerHTML = '<i class="fas fa-times"></i>';
    removeBtn.onclick = function() {
        console.log('🗑️ Eliminando contenido de caja');
        wrapper.remove();
    };
    
    wrapper.appendChild(input);
    wrapper.appendChild(removeBtn);
    container.appendChild(wrapper);
    
    console.log('✅ Nuevo contenido de caja agregado');
    
    // Enfocar el nuevo input
    input.focus();
    
    // Agregar animación
    wrapper.style.opacity = '0';
    wrapper.style.transform = 'translateY(-10px)';
    requestAnimationFrame(() => {
        wrapper.style.transition = 'all 0.3s ease';
        wrapper.style.opacity = '1';
        wrapper.style.transform = 'translateY(0)';
    });
}

function addUseCaseField() {
    console.log('🔧 Ejecutando addUseCaseField()...');
    
    const container = document.getElementById('useCasesContainer');
    
    if (!container) {
        console.error('❌ Container useCasesContainer no encontrado');
        alert('Error: No se pudo encontrar el contenedor de casos de uso');
        return;
    }
    
    console.log('✅ Container encontrado:', container);
    
    // Crear div wrapper para el input y botón eliminar
    const wrapper = document.createElement('div');
    wrapper.className = 'flex items-center space-x-2 use-case-wrapper';
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'use-case-input w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent';
    input.placeholder = 'Ej: Durante entrenamientos y ejercicio físico';
    
    // Botón para eliminar
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'text-red-600 hover:text-red-800 px-2 py-1';
    removeBtn.innerHTML = '<i class="fas fa-times"></i>';
    removeBtn.onclick = function() {
        console.log('🗑️ Eliminando caso de uso');
        wrapper.remove();
    };
    
    wrapper.appendChild(input);
    wrapper.appendChild(removeBtn);
    container.appendChild(wrapper);
    
    console.log('✅ Nuevo caso de uso agregado');
    
    // Enfocar el nuevo input
    input.focus();
    
    // Agregar animación
    wrapper.style.opacity = '0';
    wrapper.style.transform = 'translateY(-10px)';
    requestAnimationFrame(() => {
        wrapper.style.transition = 'all 0.3s ease';
        wrapper.style.opacity = '1';
        wrapper.style.transform = 'translateY(0)';
    });
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkSystemStatus();
});

function initializeApp() {
    console.log('🚀 Inicializando Creador de Listings Amazon IA');
    
    // Inicializar datos del formulario
    formData = {
        productName: '',
        category: '',
        brand: '',
        description: '',
        features: [],
        dimensions: '',
        weight: '',
        materials: '',
        color: '',
        compatibility: '',
        boxContents: [],
        targetAudience: '',
        targetPrice: 0,
        mainCompetitor: '',
        useCases: [],
        keywords: ''
    };
    
    // Configurar sistema de sugerencias
    setupSuggestionTriggers();
}

function setupEventListeners() {
    console.log('🔧 Configurando event listeners...');
    
    // Navigation buttons
    document.getElementById('nextStep1').addEventListener('click', () => validateAndNext(1));
    document.getElementById('nextStep2').addEventListener('click', () => validateAndNext(2));
    document.getElementById('nextStep3').addEventListener('click', () => validateAndNext(3));
    
    document.getElementById('backStep2').addEventListener('click', () => goToStep(1));
    document.getElementById('backStep3').addEventListener('click', () => goToStep(2));
    document.getElementById('backStep4').addEventListener('click', () => goToStep(3));
    
    // Dynamic field additions - usando un approach más robusto
    console.log('🔍 Configurando botones dinámicos...');
    
    // Event delegation para botones dinámicos
    document.addEventListener('click', function(e) {
        // Botón agregar característica
        if (e.target && (e.target.id === 'addFeature' || e.target.closest('#addFeature'))) {
            e.preventDefault();
            e.stopPropagation();
            console.log('🎯 Click en addFeature detectado');
            addFeatureField();
        }
        
        // Botón agregar contenido de caja
        if (e.target && (e.target.id === 'addBoxContent' || e.target.closest('#addBoxContent'))) {
            e.preventDefault();
            e.stopPropagation();
            console.log('🎯 Click en addBoxContent detectado');
            addBoxContentField();
        }
        
        // Botón agregar caso de uso
        if (e.target && (e.target.id === 'addUseCase' || e.target.closest('#addUseCase'))) {
            e.preventDefault();
            e.stopPropagation();
            console.log('🎯 Click en addUseCase detectado');
            addUseCaseField();
        }
    });
    
    // Configurar listeners directos también como backup
    setTimeout(() => {
        const buttons = [
            { id: 'addFeature', handler: addFeatureField },
            { id: 'addBoxContent', handler: addBoxContentField },
            { id: 'addUseCase', handler: addUseCaseField }
        ];
        
        buttons.forEach(({ id, handler }) => {
            const btn = document.getElementById(id);
            if (btn) {
                console.log(`✅ Configurando listener directo para ${id}`);
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log(`🎯 Click directo en ${id} detectado`);
                    handler();
                });
            } else {
                console.warn(`⚠️ Botón ${id} no encontrado`);
            }
        });
    }, 100);
    
    // Generate listing
    document.getElementById('generateListing').addEventListener('click', generateListing);
    
    // Generate AI suggestions
    const generateSuggestionsBtn = document.getElementById('generateSuggestions');
    if (generateSuggestionsBtn) {
        generateSuggestionsBtn.addEventListener('click', generateAISuggestions);
        console.log('✅ Event listener para generateSuggestions configurado');
    }
    
    // Final actions
    document.getElementById('backToStart').addEventListener('click', resetToStart);
    document.getElementById('saveListing').addEventListener('click', saveListing);
    document.getElementById('editListing').addEventListener('click', editListing);
    
    // Step navigation
    for (let i = 1; i <= 5; i++) {
        const stepElement = document.getElementById(`step-${i}`);
        if (stepElement) {
            stepElement.addEventListener('click', () => {
                if (i <= currentStep || currentStep === 5) {
                    goToStep(i);
                }
            });
        }
    }
}

async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/listings/health`);
        const status = await response.json();
        
        const statusElement = document.getElementById('systemStatus');
        const indicatorElement = document.getElementById('statusIndicator');
        
        if (status.system === 'healthy' && status.ollama_connected) {
            statusElement.textContent = 'Sistema listo';
            indicatorElement.className = 'w-3 h-3 rounded-full bg-green-400';
        } else {
            statusElement.textContent = 'Sistema con problemas';
            indicatorElement.className = 'w-3 h-3 rounded-full bg-red-400';
        }
    } catch (error) {
        console.error('Error checking system status:', error);
        document.getElementById('systemStatus').textContent = 'Error de conexión';
        document.getElementById('statusIndicator').className = 'w-3 h-3 rounded-full bg-red-400';
    }
}

function validateAndNext(step) {
    if (validateStep(step)) {
        collectStepData(step);
        goToStep(step + 1);
    }
}

function validateStep(step) {
    console.log(`🔍 Validando paso ${step}...`);
    let isValid = true;
    let errors = [];
    
    // Limpiar errores previos
    document.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
    document.querySelectorAll('.error-message').forEach(el => el.remove());
    
    switch (step) {
        case 1:
            // Validar nombre del producto
            const productName = document.getElementById('productName').value.trim();
            if (!productName) {
                isValid = false;
                errors.push({ field: 'productName', message: 'El nombre del producto es obligatorio' });
            } else if (productName.length < 3) {
                isValid = false;
                errors.push({ field: 'productName', message: 'El nombre debe tener al menos 3 caracteres' });
            }
            
            // Validar categoría
            const category = document.getElementById('category').value;
            if (!category) {
                isValid = false;
                errors.push({ field: 'category', message: 'Selecciona una categoría' });
            }
            
            // Validar descripción
            const description = document.getElementById('description').value.trim();
            if (!description) {
                isValid = false;
                errors.push({ field: 'description', message: 'La descripción es obligatoria' });
            } else if (description.length < 20) {
                isValid = false;
                errors.push({ field: 'description', message: 'La descripción debe tener al menos 20 caracteres' });
            }
            
            // Validar características (al menos una)
            const features = collectDynamicFields('.feature-input');
            if (features.length === 0) {
                isValid = false;
                errors.push({ field: 'featuresContainer', message: 'Agrega al menos una característica del producto' });
            }
            break;
            
        case 2:
            // Validar contenido de la caja (al menos uno)
            const boxContents = collectDynamicFields('.box-content-input');
            if (boxContents.length === 0) {
                isValid = false;
                errors.push({ field: 'boxContentsContainer', message: 'Especifica qué incluye la caja' });
            }
            break;
            
        case 3:
            // Validar audiencia objetivo
            const targetAudience = document.getElementById('targetAudience').value.trim();
            if (!targetAudience) {
                isValid = false;
                errors.push({ field: 'targetAudience', message: 'Define tu cliente objetivo' });
            }
            
            // Validar precio objetivo
            const targetPrice = parseFloat(document.getElementById('targetPrice').value);
            if (!targetPrice || targetPrice <= 0) {
                isValid = false;
                errors.push({ field: 'targetPrice', message: 'Ingresa un precio válido mayor a 0' });
            }
            
            // Validar casos de uso (al menos uno)
            const useCases = collectDynamicFields('.use-case-input');
            if (useCases.length === 0) {
                isValid = false;
                errors.push({ field: 'useCasesContainer', message: 'Agrega al menos un caso de uso' });
            }
            break;
            
        default:
            return true;
    }
    
    // Mostrar errores
    errors.forEach(error => {
        const field = document.getElementById(error.field);
        if (field) {
            field.classList.add('error');
            
            // Crear mensaje de error
            const errorMsg = document.createElement('div');
            errorMsg.className = 'error-message text-red-600 text-sm mt-1';
            errorMsg.textContent = error.message;
            
            // Insertar después del campo o su contenedor
            const container = field.closest('.form-group') || field.parentNode;
            container.appendChild(errorMsg);
            
            // Scroll al primer error
            if (errors.indexOf(error) === 0) {
                field.scrollIntoView({ behavior: 'smooth', block: 'center' });
                field.focus();
            }
        }
    });
    
    if (!isValid) {
        console.log(`❌ Validación fallida en paso ${step}:`, errors);
        showToast(`Corrige los errores marcados en rojo`, 'error');
    } else {
        console.log(`✅ Paso ${step} validado correctamente`);
    }
    
    return isValid;
}

function collectStepData(step) {
    switch (step) {
        case 1:
            formData.productName = document.getElementById('productName').value.trim();
            formData.category = document.getElementById('category').value;
            formData.brand = document.getElementById('brand').value.trim();
            formData.description = document.getElementById('description').value.trim();
            formData.features = collectDynamicFields('.feature-input');
            break;
            
        case 2:
            formData.dimensions = document.getElementById('dimensions').value.trim();
            formData.weight = document.getElementById('weight').value.trim();
            formData.materials = document.getElementById('materials').value.trim();
            formData.color = document.getElementById('color').value.trim();
            formData.compatibility = document.getElementById('compatibility').value.trim();
            formData.boxContents = collectDynamicFields('.box-content-input');
            break;
            
        case 3:
            formData.targetAudience = document.getElementById('targetAudience').value.trim();
            formData.targetPrice = parseFloat(document.getElementById('targetPrice').value) || 0;
            formData.mainCompetitor = document.getElementById('mainCompetitor').value.trim();
            formData.useCases = collectDynamicFields('.use-case-input');
            formData.keywords = document.getElementById('keywords').value.trim();
            break;
    }
    
    console.log('Datos recolectados del paso', step, ':', formData);
}

function collectDynamicFields(selector) {
    const inputs = document.querySelectorAll(selector);
    return Array.from(inputs)
        .map(input => input.value.trim())
        .filter(value => value.length > 0);
}

function goToStep(stepNumber) {
    // Ocultar todos los contenidos
    document.querySelectorAll('.step-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    // Mostrar el contenido del paso actual
    document.getElementById(`content-step-${stepNumber}`).classList.remove('hidden');
    
    // Actualizar sidebar
    updateSidebarSteps(stepNumber);
    
    // Mostrar revisión si vamos al paso 4
    if (stepNumber === 4) {
        showReview();
    }
    
    currentStep = stepNumber;
}

function updateSidebarSteps(activeStep) {
    for (let i = 1; i <= 5; i++) {
        const stepElement = document.getElementById(`step-${i}`);
        const numberElement = stepElement.querySelector('.step-number');
        
        // Resetear clases
        stepElement.className = 'step-card p-3 rounded-lg cursor-pointer';
        
        if (i < activeStep) {
            // Completado
            stepElement.classList.add('completed');
            numberElement.className = 'step-number w-6 h-6 rounded-full bg-green-500 text-white text-xs flex items-center justify-center';
            numberElement.innerHTML = '<i class="fas fa-check"></i>';
        } else if (i === activeStep) {
            // Activo
            stepElement.classList.add('active');
            numberElement.className = 'step-number w-6 h-6 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center';
            numberElement.textContent = i;
        } else {
            // Pendiente
            numberElement.className = 'step-number w-6 h-6 rounded-full bg-gray-300 text-gray-600 text-xs flex items-center justify-center';
            numberElement.textContent = i;
        }
    }
}

function showReview() {
    // Recolectar datos actuales si no se hizo
    collectStepData(3);
    
    const reviewContainer = document.getElementById('reviewContent');
    reviewContainer.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-blue-50 p-4 rounded-lg">
                <h3 class="font-semibold text-blue-800 mb-3">📝 Información Básica</h3>
                <div class="space-y-2 text-sm">
                    <div><strong>Producto:</strong> ${formData.productName}</div>
                    <div><strong>Categoría:</strong> ${formData.category}</div>
                    <div><strong>Marca:</strong> ${formData.brand || 'No especificada'}</div>
                    <div><strong>Características:</strong> ${formData.features.length} especificadas</div>
                </div>
            </div>
            
            <div class="bg-green-50 p-4 rounded-lg">
                <h3 class="font-semibold text-green-800 mb-3">🔧 Especificaciones</h3>
                <div class="space-y-2 text-sm">
                    <div><strong>Dimensiones:</strong> ${formData.dimensions || 'No especificadas'}</div>
                    <div><strong>Peso:</strong> ${formData.weight || 'No especificado'}</div>
                    <div><strong>Materiales:</strong> ${formData.materials || 'No especificados'}</div>
                    <div><strong>Contenido caja:</strong> ${formData.boxContents.length} items</div>
                </div>
            </div>
            
            <div class="bg-purple-50 p-4 rounded-lg">
                <h3 class="font-semibold text-purple-800 mb-3">🎯 Mercado Target</h3>
                <div class="space-y-2 text-sm">
                    <div><strong>Precio objetivo:</strong> $${formData.targetPrice}</div>
                    <div><strong>Competencia:</strong> ${formData.mainCompetitor || 'No especificada'}</div>
                    <div><strong>Casos de uso:</strong> ${formData.useCases.length} definidos</div>
                </div>
            </div>
            
            <div class="bg-yellow-50 p-4 rounded-lg">
                <h3 class="font-semibold text-yellow-800 mb-3">🔍 SEO & Keywords</h3>
                <div class="space-y-2 text-sm">
                    <div><strong>Keywords:</strong> ${formData.keywords || 'No especificadas'}</div>
                    <div><strong>Descripción:</strong> ${formData.description.length} caracteres</div>
                </div>
            </div>
        </div>
        
        <div class="bg-gray-50 p-4 rounded-lg mt-6">
            <h3 class="font-semibold text-gray-800 mb-2">📄 Descripción del Producto</h3>
            <p class="text-sm text-gray-600">${formData.description}</p>
        </div>
    `;
}

async function generateListing() {
    goToStep(5);
    
    // Preparar datos para la API
    const apiData = {
        product_name: formData.productName,
        description: formData.description,
        category: formData.category,
        target_price: formData.targetPrice,
        brand: formData.brand,
        features: formData.features,
        dimensions: formData.dimensions,
        weight: formData.weight,
        materials: formData.materials,
        color: formData.color,
        compatibility: formData.compatibility,
        box_contents: formData.boxContents,
        target_audience: formData.targetAudience,
        main_competitor: formData.mainCompetitor,
        use_cases: formData.useCases,
        keywords: formData.keywords.split(',').map(k => k.trim()).filter(k => k.length > 0)
    };
    
    console.log('Enviando datos a la API:', apiData);
    
    // Simular progreso de agentes
    simulateProgress();
    
    try {
        // Usar endpoint real que guarda en base de datos
        const response = await fetch(`${API_BASE}/api/listings/create-simple`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(apiData)
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const result = await response.json();
        generatedListing = result;
        
        console.log('Listing generado:', result);
        showResults(result);
        
    } catch (error) {
        console.error('Error generando listing:', error);
        showError('Error al generar el listing. Por favor intenta nuevamente.');
    }
}

function simulateProgress() {
    const progressSteps = [
        'Analizando producto y categorización...',
        'Investigando audiencia objetivo...',
        'Desarrollando propuesta de valor...',
        'Procesando especificaciones técnicas...',
        'Optimizando contenido y garantías...',
        'Calculando estrategia de precios...',
        'Optimizando SEO y palabras clave...',
        'Generando listing final...'
    ];
    
    const container = document.getElementById('progressSteps');
    let currentProgressStep = 0;
    
    const progressInterval = setInterval(() => {
        if (currentProgressStep < progressSteps.length) {
            // Marcar paso anterior como completado
            if (currentProgressStep > 0) {
                const prevStep = container.children[currentProgressStep - 1];
                prevStep.innerHTML = `
                    <div class="flex items-center text-green-600">
                        <i class="fas fa-check-circle mr-3"></i>
                        <span>${progressSteps[currentProgressStep - 1]}</span>
                    </div>
                `;
            }
            
            // Agregar nuevo paso si no es el primero
            if (currentProgressStep < progressSteps.length) {
                if (currentProgressStep > 0) {
                    const newStep = document.createElement('div');
                    newStep.innerHTML = `
                        <div class="flex items-center text-blue-600">
                            <div class="loader mr-3" style="width: 16px; height: 16px; border-width: 2px;"></div>
                            <span>${progressSteps[currentProgressStep]}</span>
                        </div>
                    `;
                    container.appendChild(newStep);
                } else {
                    // Actualizar el primer paso
                    container.children[0].innerHTML = `
                        <div class="flex items-center text-blue-600">
                            <div class="loader mr-3" style="width: 16px; height: 16px; border-width: 2px;"></div>
                            <span>${progressSteps[currentProgressStep]}</span>
                        </div>
                    `;
                }
            }
            
            currentProgressStep++;
        } else {
            clearInterval(progressInterval);
        }
    }, 2000);
}

function showResults(listing) {
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('resultsState').classList.remove('hidden');
    
    const resultsContainer = document.getElementById('listingResults');
    resultsContainer.innerHTML = `
        <div class="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
            <div class="flex items-center mb-4">
                <i class="fas fa-check-circle text-green-500 text-xl mr-3"></i>
                <h3 class="text-lg font-semibold text-green-800">Listing generado exitosamente</h3>
                <span class="ml-auto bg-green-500 text-white px-3 py-1 rounded-full text-sm">
                    Confidence: ${Math.round((listing.confidence_score || 0.85) * 100)}%
                </span>
            </div>
            ${listing.database_id ? `<p class="text-sm text-green-600">Guardado en base de datos con ID: ${listing.database_id}</p>` : ''}
        </div>
        
        <div class="space-y-6">
            <div class="bg-white border rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-3">🏷️ Título Optimizado</h3>
                <div class="bg-blue-50 p-4 rounded-lg">
                    <p class="font-medium text-blue-900">${listing.title || 'Título no generado'}</p>
                </div>
            </div>
            
            <div class="bg-white border rounded-lg p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-3">📋 Bullet Points</h3>
                <div class="space-y-2">
                    ${(listing.bullet_points || []).map(point => `
                        <div class="bg-gray-50 p-3 rounded-lg">
                            <p class="text-gray-800">${point}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white border rounded-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-3">🔍 Search Terms</h3>
                    <div class="flex flex-wrap gap-2">
                        ${(listing.search_terms || []).map(term => `
                            <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">${term}</span>
                        `).join('')}
                    </div>
                </div>
                
                <div class="bg-white border rounded-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-3">🎯 Backend Keywords</h3>
                    <div class="flex flex-wrap gap-2">
                        ${(listing.backend_keywords || []).map(keyword => `
                            <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">${keyword}</span>
                        `).join('')}
                    </div>
                </div>
            </div>
            
            ${listing.recommendations && listing.recommendations.length > 0 ? `
                <div class="bg-white border rounded-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-3">💡 Recomendaciones</h3>
                    <div class="space-y-2">
                        ${listing.recommendations.map(rec => `
                            <div class="flex items-start">
                                <i class="fas fa-lightbulb text-yellow-500 mt-1 mr-3"></i>
                                <p class="text-gray-700">${rec}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

function showError(message) {
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('resultsState').classList.remove('hidden');
    
    const resultsContainer = document.getElementById('listingResults');
    resultsContainer.innerHTML = `
        <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <i class="fas fa-exclamation-triangle text-red-500 text-3xl mb-4"></i>
            <h3 class="text-lg font-semibold text-red-800 mb-2">Error al generar listing</h3>
            <p class="text-red-600">${message}</p>
            <button onclick="goToStep(4)" class="mt-4 bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg">
                Intentar nuevamente
            </button>
        </div>
    `;
}

function resetToStart() {
    currentStep = 1;
    formData = {};
    generatedListing = null;
    
    // Limpiar todos los formularios
    document.querySelectorAll('input, textarea, select').forEach(input => {
        input.value = '';
    });
    
    // Limpiar campos dinámicos
    document.getElementById('featuresContainer').innerHTML = `
        <input type="text" class="feature-input w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="Ej: Batería de 7 días de duración">
    `;
    
    document.getElementById('boxContentsContainer').innerHTML = `
        <input type="text" class="box-content-input w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="Ej: 1x Smartwatch">
    `;
    
    document.getElementById('useCasesContainer').innerHTML = `
        <input type="text" class="use-case-input w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="Ej: Durante entrenamientos y ejercicio físico">
    `;
    
    // Reset loading state
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('resultsState').classList.add('hidden');
    
    goToStep(1);
    showToast('Formulario reiniciado', 'success');
}

async function saveListing() {
    if (!generatedListing) {
        showToast('No hay listing para guardar', 'error');
        return;
    }
    
    try {
        // El listing ya está guardado automáticamente al generarlo
        const dbId = generatedListing.database_id;
        
        if (dbId) {
            showToast(`✅ Listing guardado en la base de datos (ID: ${dbId})`, 'success');
            
            // Agregar enlace para ver listings
            setTimeout(() => {
                const confirmation = confirm('¿Quieres ver todos los listings guardados?');
                if (confirmation) {
                    window.location.href = 'listings.html';
                }
            }, 1500);
        } else {
            showToast('⚠️ El listing se generó pero no se pudo confirmar el guardado', 'warning');
        }
        
    } catch (error) {
        console.error('Error saving listing:', error);
        showToast('Error al guardar el listing', 'error');
    }
}

function editListing() {
    // Volver al paso de revisión para permitir ediciones
    goToStep(4);
    showToast('Puedes modificar la información y regenerar el listing', 'info');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    
    // Cambiar color según tipo
    toast.className = 'fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300';
    
    switch (type) {
        case 'success':
            toast.classList.add('bg-green-500', 'text-white');
            break;
        case 'error':
            toast.classList.add('bg-red-500', 'text-white');
            break;
        case 'info':
            toast.classList.add('bg-blue-500', 'text-white');
            break;
        default:
            toast.classList.add('bg-gray-500', 'text-white');
    }
    
    // Mostrar toast
    toast.classList.remove('hidden', 'translate-y-full');
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        toast.classList.add('translate-y-full');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 300);
    }, 3000);
}

// Funciones de sugerencias automáticas
let suggestionsCache = null;

async function generateSuggestions(productName, description) {
    if (!productName || !description) {
        console.warn('⚠️ No se puede generar sugerencias sin nombre y descripción');
        return null;
    }
    
    try {
        console.log('🤖 Generando sugerencias para:', productName);
        console.log('📝 Descripción:', description);
        console.log('🔗 URL del endpoint:', `${API_BASE}/api/listings/suggestions`);
        
        const response = await fetch(`${API_BASE}/api/listings/suggestions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_name: productName,
                description: description
            })
        });
        
        console.log('📡 Respuesta del servidor - Status:', response.status);
        console.log('📡 Respuesta del servidor - OK:', response.ok);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Error del servidor:', errorText);
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }
        
        const data = await response.json();
        console.log('📊 Datos recibidos:', data);
        
        if (data.success) {
            suggestionsCache = data.suggestions;
            console.log('✅ Sugerencias guardadas en cache:', suggestionsCache);
            return suggestionsCache;
        } else {
            console.warn('⚠️ Usando sugerencias de fallback');
            console.log('📋 Fallback data:', data.fallback_suggestions);
            suggestionsCache = data.fallback_suggestions;
            return suggestionsCache;
        }
        
    } catch (error) {
        console.error('❌ Error generando sugerencias:', error);
        showToast('Error generando sugerencias automáticas', 'error');
        return null;
    }
}

function applySuggestions() {
    console.log('🎯 Intentando aplicar sugerencias...');
    console.log('📦 suggestionsCache:', suggestionsCache);
    
    if (!suggestionsCache) {
        console.warn('⚠️ No hay sugerencias disponibles en cache');
        showToast('No hay sugerencias disponibles. Intenta generar primero.', 'error');
        return;
    }
    
    console.log('✅ Aplicando sugerencias:', suggestionsCache);
    const suggestions = suggestionsCache;
    
    // Aplicar sugerencias al paso 1
    applySuggestionsStep1(suggestions);
    
    // Aplicar sugerencias al paso 2
    applySuggestionsStep2(suggestions);
    
    // Aplicar sugerencias al paso 3
    applySuggestionsStep3(suggestions);
    
    showToast('Sugerencias aplicadas automáticamente', 'success');
}

function applySuggestionsStep1(suggestions) {
    // Categoría
    const categorySelect = document.getElementById('category');
    if (categorySelect && suggestions.category) {
        // Buscar opción que coincida
        for (let option of categorySelect.options) {
            if (option.value.toLowerCase().includes(suggestions.category.toLowerCase()) ||
                suggestions.category.toLowerCase().includes(option.value.toLowerCase())) {
                option.selected = true;
                break;
            }
        }
    }
    
    // Marca
    const brandInput = document.getElementById('brand');
    if (brandInput && suggestions.brand) {
        brandInput.value = suggestions.brand;
        brandInput.style.backgroundColor = '#f0f9ff';
        setTimeout(() => brandInput.style.backgroundColor = '', 2000);
    }
    
    // Características
    if (suggestions.features && suggestions.features.length > 0) {
        const featuresContainer = document.getElementById('featuresContainer');
        if (featuresContainer) {
            // Limpiar características existentes (excepto la primera)
            const existingFeatures = featuresContainer.querySelectorAll('.feature-wrapper');
            existingFeatures.forEach((feature, index) => {
                if (index > 0) feature.remove();
            });
            
            // Llenar primera característica
            const firstInput = featuresContainer.querySelector('.feature-input');
            if (firstInput) {
                firstInput.value = suggestions.features[0];
                firstInput.style.backgroundColor = '#f0f9ff';
                setTimeout(() => firstInput.style.backgroundColor = '', 2000);
            }
            
            // Agregar características adicionales
            for (let i = 1; i < suggestions.features.length && i < 5; i++) {
                addFeatureField();
                const newInputs = featuresContainer.querySelectorAll('.feature-input');
                const newInput = newInputs[newInputs.length - 1];
                if (newInput) {
                    newInput.value = suggestions.features[i];
                    newInput.style.backgroundColor = '#f0f9ff';
                    setTimeout(() => newInput.style.backgroundColor = '', 2000);
                }
            }
        }
    }
}

function applySuggestionsStep2(suggestions) {
    // Dimensiones
    const dimensionsInput = document.getElementById('dimensions');
    if (dimensionsInput && suggestions.dimensions) {
        dimensionsInput.value = suggestions.dimensions;
        dimensionsInput.style.backgroundColor = '#f0f9ff';
        setTimeout(() => dimensionsInput.style.backgroundColor = '', 2000);
    }
    
    // Peso
    const weightInput = document.getElementById('weight');
    if (weightInput && suggestions.weight) {
        weightInput.value = suggestions.weight;
        weightInput.style.backgroundColor = '#f0f9ff';
        setTimeout(() => weightInput.style.backgroundColor = '', 2000);
    }
    
    // Materiales
    const materialsInput = document.getElementById('materials');
    if (materialsInput && suggestions.materials) {
        materialsInput.value = suggestions.materials;
        materialsInput.style.backgroundColor = '#f0f9ff';
        setTimeout(() => materialsInput.style.backgroundColor = '', 2000);
    }
    
    // Color
    const colorInput = document.getElementById('color');
    if (colorInput && suggestions.colors && suggestions.colors.length > 0) {
        colorInput.value = suggestions.colors[0];
        colorInput.style.backgroundColor = '#f0f9ff';
        setTimeout(() => colorInput.style.backgroundColor = '', 2000);
    }
    
    // Aplicar a campos dinámicos de especificaciones
    applyToBoxContentFields(suggestions);
}

function applySuggestionsStep3(suggestions) {
    // Audiencia objetivo
    const targetAudienceInput = document.getElementById('targetAudience');
    if (targetAudienceInput && suggestions.target_audience) {
        targetAudienceInput.value = suggestions.target_audience;
        targetAudienceInput.style.backgroundColor = '#f0f9ff';
        setTimeout(() => targetAudienceInput.style.backgroundColor = '', 2000);
    }
    
    // Precio sugerido
    const targetPriceInput = document.getElementById('targetPrice');
    if (targetPriceInput && suggestions.price_range && suggestions.price_range.suggested) {
        targetPriceInput.value = suggestions.price_range.suggested;
        targetPriceInput.style.backgroundColor = '#f0f9ff';
        setTimeout(() => targetPriceInput.style.backgroundColor = '', 2000);
    }
    
    // Competidor principal
    const mainCompetitorInput = document.getElementById('mainCompetitor');
    if (mainCompetitorInput && suggestions.main_competitor) {
        mainCompetitorInput.value = suggestions.main_competitor;
        mainCompetitorInput.style.backgroundColor = '#f0f9ff';
        setTimeout(() => mainCompetitorInput.style.backgroundColor = '', 2000);
    }
    
    // Keywords/palabras clave
    const keywordsInput = document.getElementById('keywords');
    if (keywordsInput && suggestions.keywords && suggestions.keywords.length > 0) {
        keywordsInput.value = suggestions.keywords.join(', ');
        keywordsInput.style.backgroundColor = '#f0f9ff';
        setTimeout(() => keywordsInput.style.backgroundColor = '', 2000);
    }
    
    // Casos de uso
    if (suggestions.use_cases && suggestions.use_cases.length > 0) {
        applyToUseCaseFields(suggestions.use_cases);
    }
}

function applyToBoxContentFields(suggestions) {
    // Usar contenidos de caja específicos si están disponibles, sino usar bullet points
    const boxContents = suggestions.box_contents || suggestions.bullet_points || [];
    
    if (boxContents.length > 0) {
        const boxContentContainer = document.getElementById('boxContentsContainer');
        if (boxContentContainer) {
            // Limpiar contenidos existentes (excepto el primero)
            const existingContents = boxContentContainer.querySelectorAll('.box-content-wrapper');
            existingContents.forEach((content, index) => {
                if (index > 0) content.remove();
            });
            
            // Llenar primer contenido
            const firstInput = boxContentContainer.querySelector('.box-content-input');
            if (firstInput) {
                firstInput.value = boxContents[0];
                firstInput.style.backgroundColor = '#f0f9ff';
                setTimeout(() => firstInput.style.backgroundColor = '', 2000);
            }
            
            // Agregar contenidos adicionales
            for (let i = 1; i < boxContents.length && i < 5; i++) {
                addBoxContentField();
                const newInputs = boxContentContainer.querySelectorAll('.box-content-input');
                const newInput = newInputs[newInputs.length - 1];
                if (newInput) {
                    newInput.value = boxContents[i];
                    newInput.style.backgroundColor = '#f0f9ff';
                    setTimeout(() => newInput.style.backgroundColor = '', 2000);
                }
            }
        }
    }
}

function applyToUseCaseFields(useCases) {
    const useCaseContainer = document.getElementById('useCasesContainer');
    if (useCaseContainer && useCases && useCases.length > 0) {
        // Limpiar casos de uso existentes (excepto el primero)
        const existingUseCases = useCaseContainer.querySelectorAll('.use-case-wrapper');
        existingUseCases.forEach((useCase, index) => {
            if (index > 0) useCase.remove();
        });
        
        // Llenar primer caso de uso
        const firstInput = useCaseContainer.querySelector('.use-case-input');
        if (firstInput) {
            firstInput.value = useCases[0];
            firstInput.style.backgroundColor = '#f0f9ff';
            setTimeout(() => firstInput.style.backgroundColor = '', 2000);
        }
        
        // Agregar casos de uso adicionales
        for (let i = 1; i < useCases.length && i < 5; i++) {
            addUseCaseField();
            const newInputs = useCaseContainer.querySelectorAll('.use-case-input');
            const newInput = newInputs[newInputs.length - 1];
            if (newInput) {
                newInput.value = useCases[i];
                newInput.style.backgroundColor = '#f0f9ff';
                setTimeout(() => newInput.style.backgroundColor = '', 2000);
            }
        }
    }
}

// Función para monitorear cambios en nombre y descripción
function setupSuggestionTriggers() {
    const productNameInput = document.getElementById('productName');
    const descriptionInput = document.getElementById('description');
    
    let suggestionTimeout;
    
    function triggerSuggestions() {
        const productName = productNameInput?.value?.trim();
        const description = descriptionInput?.value?.trim();
        
        console.log('🔍 Verificando triggers - Nombre:', productName?.length, 'Descripción:', description?.length);
        
        if (productName && description && productName.length > 3 && description.length > 10) {
            console.log('✅ Condiciones cumplidas, programando sugerencias...');
            clearTimeout(suggestionTimeout);
            suggestionTimeout = setTimeout(async () => {
                console.log('🤖 Activando sugerencias automáticas...');
                const result = await generateSuggestions(productName, description);
                console.log('🎯 Resultado de sugerencias:', result);
                if (result) {
                    showSuggestionButtons();
                }
            }, 2000); // Esperar 2 segundos después del último cambio
        } else {
            console.log('❌ Condiciones no cumplidas para generar sugerencias');
        }
    }
    
    if (productNameInput) {
        productNameInput.addEventListener('input', triggerSuggestions);
    }
    
    if (descriptionInput) {
        descriptionInput.addEventListener('input', triggerSuggestions);
    }
}

function showSuggestionToast(suggestions) {
    if (suggestions) {
        const categories = [];
        if (suggestions.features?.length) categories.push(`${suggestions.features.length} características`);
        if (suggestions.use_cases?.length) categories.push(`${suggestions.use_cases.length} casos de uso`);
        if (suggestions.keywords?.length) categories.push(`${suggestions.keywords.length} keywords`);
        if (suggestions.box_contents?.length) categories.push(`${suggestions.box_contents.length} contenidos`);
        
        const message = `✨ Sugerencias generadas: ${categories.join(', ')}`;
        showToast(message, 'success');
    }
}

function showSuggestionButtons() {
    // Agregar botón de aplicar sugerencias si no existe
    let suggestionBtn = document.getElementById('applySuggestionsBtn');
    if (!suggestionBtn) {
        suggestionBtn = document.createElement('button');
        suggestionBtn.id = 'applySuggestionsBtn';
        suggestionBtn.type = 'button';
        suggestionBtn.className = 'ml-4 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors';
        suggestionBtn.innerHTML = '<i class="fas fa-magic mr-2"></i>Aplicar Sugerencias IA';
        suggestionBtn.onclick = applySuggestions;
        
        // Agregar después del botón "Siguiente"
        const nextBtn = document.getElementById('nextStep1');
        if (nextBtn && nextBtn.parentNode) {
            nextBtn.parentNode.insertBefore(suggestionBtn, nextBtn);
        }
    }
    
    // Mostrar información sobre las sugerencias disponibles
    if (suggestionsCache) {
        showSuggestionToast(suggestionsCache);
    }
    
    // Mostrar animación de disponibilidad
    suggestionBtn.style.animation = 'pulse 1s infinite';
    setTimeout(() => {
        suggestionBtn.style.animation = '';
    }, 3000);
}

// Función de utilidad para debug de sugerencias
window.debugSuggestions = () => {
    console.log('Cached suggestions:', suggestionsCache);
    if (suggestionsCache) {
        applySuggestions();
    }
};

// Función de utilidad para debug
window.debugFormData = () => {
    console.log('Current form data:', formData);
    console.log('Generated listing:', generatedListing);
};

// Función específica para el botón de sugerencias con IA
async function generateAISuggestions() {
    console.log('🎯 Iniciando generación de sugerencias IA...');
    
    // Obtener datos del formulario
    const productName = document.getElementById('productName')?.value?.trim();
    const description = document.getElementById('description')?.value?.trim();
    
    // Validar campos requeridos
    if (!productName) {
        showToast('Por favor, ingresa el nombre del producto primero', 'warning');
        document.getElementById('productName')?.focus();
        return;
    }
    
    if (!description) {
        showToast('Por favor, ingresa la descripción del producto primero', 'warning');
        document.getElementById('description')?.focus();
        return;
    }
    
    // UI Updates - Mostrar estado de carga
    const button = document.getElementById('generateSuggestions');
    const buttonText = document.getElementById('suggestionsButtonText');
    const buttonLoading = document.getElementById('suggestionsButtonLoading');
    const statusDiv = document.getElementById('suggestionsStatus');
    const statusText = document.getElementById('suggestionsStatusText');
    
    if (button) button.disabled = true;
    if (buttonText) buttonText.classList.add('hidden');
    if (buttonLoading) buttonLoading.classList.remove('hidden');
    if (statusDiv) statusDiv.classList.remove('hidden');
    if (statusText) statusText.textContent = 'Conectando con nuestros agentes de IA...';
    
    try {
        // Generar sugerencias
        const suggestions = await generateSuggestions(productName, description);
        
        if (suggestions) {
            // Aplicar sugerencias automáticamente
            applySuggestions();
            
            // UI Success
            if (statusText) statusText.textContent = `¡Sugerencias aplicadas! Se completaron automáticamente ${Object.keys(suggestions).length} campos.`;
            showToast('¡Sugerencias aplicadas exitosamente! Revisa los campos completados.', 'success');
            
            // Auto-hide status after 5 seconds
            setTimeout(() => {
                if (statusDiv) statusDiv.classList.add('hidden');
            }, 5000);
            
        } else {
            throw new Error('No se pudieron generar sugerencias');
        }
        
    } catch (error) {
        console.error('❌ Error en generateAISuggestions:', error);
        
        // UI Error
        if (statusText) statusText.textContent = 'Error al generar sugerencias. Intenta de nuevo.';
        showToast('Error al generar sugerencias automáticas. Verifica tu conexión.', 'error');
        
        // Auto-hide status after 3 seconds
        setTimeout(() => {
            if (statusDiv) statusDiv.classList.add('hidden');
        }, 3000);
        
    } finally {
        // Restaurar botón
        if (button) button.disabled = false;
        if (buttonText) buttonText.classList.remove('hidden');
        if (buttonLoading) buttonLoading.classList.add('hidden');
    }
}

// Hacer la función disponible globalmente para onclick
window.generateAISuggestions = generateAISuggestions;
