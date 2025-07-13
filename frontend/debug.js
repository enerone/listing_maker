// Script de debug para el frontend
// Ejecutar en la consola del navegador

console.log('🔍 === SCRIPT DE DEBUG PARA BOTONES ===');

// Verificar si los elementos existen
console.log('addFeature button:', document.getElementById('addFeature'));
console.log('addBoxContent button:', document.getElementById('addBoxContent'));
console.log('addUseCase button:', document.getElementById('addUseCase'));

// Verificar si las funciones están disponibles
console.log('addFeatureField function:', typeof window.addFeatureField);
console.log('addBoxContentField function:', typeof window.addBoxContentField);
console.log('addUseCaseField function:', typeof window.addUseCaseField);

// Agregar listener directo para probar
const btn = document.getElementById('addFeature');
if (btn) {
    console.log('✅ Botón encontrado, agregando listener directo...');
    btn.addEventListener('click', function(e) {
        console.log('🎯 Listener directo - Click detectado!');
        if (typeof window.addFeatureField === 'function') {
            window.addFeatureField();
        } else {
            console.error('❌ Función addFeatureField no disponible');
        }
    });
} else {
    console.error('❌ Botón addFeature no encontrado');
}

// Función de prueba manual
window.testAddFeature = function() {
    console.log('🧪 Ejecutando test manual...');
    if (typeof window.addFeatureField === 'function') {
        window.addFeatureField();
    } else {
        console.error('❌ Función no disponible');
    }
};

console.log('✅ Debug script cargado. Ejecuta testAddFeature() para probar manualmente.');
