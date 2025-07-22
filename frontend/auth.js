// auth.js - Utilidades para autenticación
class AuthManager {
    constructor() {
        this.API_BASE = '/auth/api/auth';
    }

    // Obtener token almacenado
    getToken() {
        return localStorage.getItem('access_token');
    }

    // Obtener información del usuario
    getUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }

    // Verificar si el usuario está logueado
    isLoggedIn() {
        return this.getToken() !== null;
    }

    // Cerrar sesión
    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/auth';
    }

    // Obtener headers con autorización
    getAuthHeaders() {
        const token = this.getToken();
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }

    // Hacer petición autenticada
    async fetchWithAuth(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...this.getAuthHeaders(),
                ...options.headers
            }
        });

        // Si la respuesta es 401 (no autorizado), redirigir al login
        if (response.status === 401) {
            this.logout();
            return;
        }

        return response;
    }

    // Crear componente de usuario en el header
    createUserComponent() {
        const user = this.getUser();
        if (!user) {
            return `
                <div class="auth-section">
                    <a href="/auth" class="auth-link">🔐 Iniciar Sesión</a>
                </div>
            `;
        }

        return `
            <div class="user-section">
                <div class="user-info">
                    <span class="user-name">👤 ${user.full_name || user.username}</span>
                    <span class="user-email">${user.email}</span>
                </div>
                <div class="user-actions">
                    <button onclick="authManager.logout()" class="logout-btn">
                        🚪 Cerrar Sesión
                    </button>
                </div>
            </div>
        `;
    }

    // Inyectar estilos para el componente de usuario
    injectUserStyles() {
        if (document.getElementById('auth-styles')) return;

        const styles = `
            <style id="auth-styles">
                .auth-section, .user-section {
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    padding: 10px;
                }

                .auth-link {
                    color: #3498db;
                    text-decoration: none;
                    font-weight: 600;
                    padding: 8px 16px;
                    border: 2px solid #3498db;
                    border-radius: 20px;
                    transition: all 0.3s ease;
                }

                .auth-link:hover {
                    background: #3498db;
                    color: white;
                }

                .user-section {
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 10px 15px;
                    max-width: 300px;
                }

                .user-info {
                    display: flex;
                    flex-direction: column;
                    margin-right: 15px;
                }

                .user-name {
                    font-weight: 600;
                    color: #2c3e50;
                    font-size: 14px;
                }

                .user-email {
                    font-size: 12px;
                    color: #666;
                    margin-top: 2px;
                }

                .logout-btn {
                    background: #e74c3c;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 5px;
                    font-size: 12px;
                    cursor: pointer;
                    transition: background 0.3s ease;
                }

                .logout-btn:hover {
                    background: #c0392b;
                }

                @media (max-width: 768px) {
                    .user-section {
                        max-width: 200px;
                    }
                    
                    .user-name, .user-email {
                        font-size: 12px;
                    }
                    
                    .logout-btn {
                        padding: 4px 8px;
                        font-size: 11px;
                    }
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
    }

    // Inicializar componente de usuario (llamar al cargar la página)
    init() {
        this.injectUserStyles();
        
        // Buscar container para el componente de usuario
        const authContainer = document.getElementById('auth-container');
        if (authContainer) {
            authContainer.innerHTML = this.createUserComponent();
        }

        // También buscar en el header si existe
        const header = document.querySelector('header, .header, .navbar');
        if (header && !authContainer) {
            const userComponent = document.createElement('div');
            userComponent.id = 'auth-container';
            userComponent.innerHTML = this.createUserComponent();
            header.appendChild(userComponent);
        }
    }
}

// Crear instancia global
const authManager = new AuthManager();

// Inicializar automáticamente cuando se carga el DOM
document.addEventListener('DOMContentLoaded', () => {
    authManager.init();
});

// También inicializar si el script se carga después del DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => authManager.init());
} else {
    authManager.init();
}
