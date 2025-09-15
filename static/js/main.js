// ===== CONFIGURACIÓN GLOBAL =====
const CONFIG = {
    animationDuration: 300,
    autoHideDelay: 5000,
    loadingTimeout: 3000,
    scrollThreshold: 300
};

// ===== CLASE PRINCIPAL DE LA APLICACIÓN =====
class TuSolucionApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        console.log('🎨 Tu Solución - Sistema de Gestión de Catering inicializado!');
    }

    setupEventListeners() {
        // Scroll to top
        this.setupScrollToTop();
        
        // Form validation
        this.setupFormValidation();
        
        // Auto-hide alerts
        this.setupAutoHideAlerts();
        
        // Loading screen
        this.setupLoadingScreen();
        
        // Character counters
        this.setupCharacterCounters();
        
        // Tooltips
        this.setupTooltips();
    }

    initializeComponents() {
        // Initialize Bootstrap components
        this.initializeBootstrapComponents();
    }

    // ===== SCROLL TO TOP =====
    setupScrollToTop() {
        const scrollBtn = document.getElementById('scroll-to-top');
        if (!scrollBtn) return;

        window.addEventListener('scroll', () => {
            if (window.pageYOffset > CONFIG.scrollThreshold) {
                scrollBtn.classList.add('show');
            } else {
                scrollBtn.classList.remove('show');
            }
        });

        scrollBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // ===== FORM VALIDATION =====
    setupFormValidation() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.showNotification('Por favor, complete todos los campos requeridos.', 'warning');
                }
            });

            // Real-time validation
            form.querySelectorAll('input, select, textarea').forEach(field => {
                field.addEventListener('blur', () => this.validateField(field));
                field.addEventListener('input', () => this.clearFieldError(field));
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required');
        const type = field.type;
        let isValid = true;

        this.clearFieldError(field);

        if (isRequired && !value) {
            this.showFieldError(field, 'Este campo es requerido');
            isValid = false;
        }

        if (type === 'email' && value && !this.isValidEmail(value)) {
            this.showFieldError(field, 'Ingresa un email válido');
            isValid = false;
        }

        if (type === 'number' && value && isNaN(value)) {
            this.showFieldError(field, 'Ingresa un número válido');
            isValid = false;
        }

        return isValid;
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        let errorDiv = field.parentElement.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentElement.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentElement.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // ===== AUTO-HIDE ALERTS =====
    setupAutoHideAlerts() {
        document.querySelectorAll('.alert').forEach(alert => {
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.style.opacity = '0';
                    setTimeout(() => {
                        if (alert.parentElement) {
                            alert.remove();
                        }
                    }, 300);
                }
            }, CONFIG.autoHideDelay);
        });
    }

    // ===== LOADING SCREEN =====
    setupLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            // Ocultar inmediatamente para evitar problemas de carga
            setTimeout(() => {
                loadingScreen.style.opacity = '0';
                setTimeout(() => {
                    loadingScreen.style.display = 'none';
                }, 300);
            }, 100);
            
            // También ocultar cuando la página esté completamente cargada
            window.addEventListener('load', () => {
                loadingScreen.style.opacity = '0';
                setTimeout(() => {
                    loadingScreen.style.display = 'none';
                }, 300);
            });
        }
    }

    // ===== CHARACTER COUNTERS =====
    setupCharacterCounters() {
        document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
            const counter = document.createElement('div');
            counter.className = 'character-counter text-muted small mt-1';
            counter.textContent = `0/${textarea.getAttribute('maxlength')}`;
            textarea.parentElement.appendChild(counter);
            
            textarea.addEventListener('input', () => {
                const currentLength = textarea.value.length;
                const maxLength = textarea.getAttribute('maxlength');
                counter.textContent = `${currentLength}/${maxLength}`;
                
                if (currentLength > maxLength * 0.9) {
                    counter.style.color = 'var(--danger)';
                } else {
                    counter.style.color = 'var(--gray-500)';
                }
            });
        });
    }

    // ===== TOOLTIPS =====
    setupTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // ===== BOOTSTRAP COMPONENTS =====
    initializeBootstrapComponents() {
        // Initialize any Bootstrap components that need it
        // This is a placeholder for future Bootstrap component initialization
    }

    // ===== NOTIFICATIONS =====
    showNotification(message, type = 'info', duration = CONFIG.autoHideDelay) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="bi bi-${this.getNotificationIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            setTimeout(() => {
                if (alertDiv.parentElement) {
                    alertDiv.style.opacity = '0';
                    setTimeout(() => {
                        if (alertDiv.parentElement) {
                            alertDiv.remove();
                        }
                    }, 300);
                }
            }, duration);
        }
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            warning: 'exclamation-triangle',
            danger: 'x-circle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }

    // ===== LOADING STATES =====
    showLoading(element) {
        if (element) {
            const originalContent = element.innerHTML;
            element.innerHTML = '<span class="loading-spinner"></span> Cargando...';
            element.disabled = true;
            return originalContent;
        }
    }

    hideLoading(element, originalContent) {
        if (element && originalContent) {
            element.innerHTML = originalContent;
            element.disabled = false;
        }
    }

    // ===== UTILITY FUNCTIONS =====
    debounce(func, wait) {
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

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// ===== FUNCIONES AJAX =====
function verificarDisponibilidad(fecha) {
    return new Promise((resolve, reject) => {
        fetch(`/api/verificar-disponibilidad/?fecha=${fecha}`)
            .then(response => response.json())
            .then(data => resolve(data))
            .catch(error => reject(error));
    });
}

function cargarProductos(tipoProducto) {
    return new Promise((resolve, reject) => {
        // Verificar si existe el elemento antes de hacer la petición
        const productoSelect = document.getElementById('id_id_producto');
        if (!productoSelect) {
            console.log('ℹ️ Elemento id_id_producto no encontrado, saltando carga de productos');
            resolve({ productos: [] });
            return;
        }

        const url = `/api/productos-por-tipo/?tipo_id=${tipoProducto}`;
        
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Actualizar el select de productos
                if (productoSelect) {
                    // Limpiar opciones existentes
                    productoSelect.innerHTML = '<option value="">Seleccione un producto</option>';
                    
                    // Agregar nuevas opciones
                    if (data.productos && data.productos.length > 0) {
                        data.productos.forEach(producto => {
                            const option = document.createElement('option');
                            option.value = producto.id_producto;
                            option.textContent = `${producto.descripcion} - $${producto.precio}`;
                            productoSelect.appendChild(option);
                        });
                    } else {
                        const option = document.createElement('option');
                        option.value = '';
                        option.textContent = 'No hay productos disponibles para este tipo';
                        productoSelect.appendChild(option);
                    }
                }
                resolve(data);
            })
            .catch(error => {
                console.error('Error al cargar productos:', error);
                if (productoSelect) {
                    productoSelect.innerHTML = '<option value="">Error al cargar productos</option>';
                }
                reject(error);
            });
    });
}

// ===== INICIALIZACIÓN =====
let app;

document.addEventListener('DOMContentLoaded', function() {
    app = new TuSolucionApp();
});

// ===== FUNCIONES GLOBALES =====
window.showNotification = function(message, type = 'info', duration = 5000) {
    if (app) {
        app.showNotification(message, type, duration);
    }
};

window.showLoading = function(element) {
    if (app) {
        return app.showLoading(element);
    }
};

window.hideLoading = function(element, originalContent) {
    if (app) {
        app.hideLoading(element, originalContent);
    }
};

window.verificarDisponibilidad = verificarDisponibilidad;
window.cargarProductos = cargarProductos;
