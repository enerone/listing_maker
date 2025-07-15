// config.js - Configuración dinámica para el frontend
class Config {
    static getApiBaseUrl() {
        // La API siempre está en el puerto 8000
        const apiPort = '8000';
        const currentHost = window.location.hostname || 'localhost';
        const currentProtocol = window.location.protocol || 'http:';
        
        return `${currentProtocol}//${currentHost}:${apiPort}`;
    }
    
    static getApiUrl(endpoint) {
        return `${this.getApiBaseUrl()}${endpoint}`;
    }
}

// Exportar para uso global
window.Config = Config;

// Por compatibilidad, también definir API_BASE_URL global
window.API_BASE_URL = Config.getApiBaseUrl();

console.log('API Base URL configurada dinámicamente:', window.API_BASE_URL);
