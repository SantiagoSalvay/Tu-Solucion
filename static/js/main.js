// Funcionalidades básicas de JavaScript para Tu Solución

// Auto-hide para alertas después de 5 segundos
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Tooltip initialization
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Form validation feedback
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// Función para verificar disponibilidad de fecha
function verificarDisponibilidad(fecha) {
    if (!fecha) return;
    
    fetch(`/api/verificar-disponibilidad/?fecha=${fecha}`)
        .then(response => response.json())
        .then(data => {
            var disponibilidadElement = document.getElementById('disponibilidad');
            if (disponibilidadElement) {
                if (data.disponible) {
                    disponibilidadElement.innerHTML = '<span class="text-success"><i class="bi bi-check-circle"></i> Disponible</span>';
                } else {
                    disponibilidadElement.innerHTML = '<span class="text-danger"><i class="bi bi-x-circle"></i> No disponible</span>';
                }
            }
        })
        .catch(error => console.error('Error:', error));
}

// Función para cargar productos por tipo
function cargarProductos(tipoId) {
    if (!tipoId) return;
    
    fetch(`/api/productos-por-tipo/?tipo_id=${tipoId}`)
        .then(response => response.json())
        .then(data => {
            var productoSelect = document.getElementById('producto');
            if (productoSelect) {
                productoSelect.innerHTML = '<option value="">Seleccione un producto</option>';
                data.productos.forEach(function(producto) {
                    var option = document.createElement('option');
                    option.value = producto.id_producto;
                    option.textContent = `${producto.descripcion} - $${producto.precio}`;
                    productoSelect.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Error:', error));
}
