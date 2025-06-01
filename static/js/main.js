// JavaScript principal para Club Manager

// Inicialización de tooltips de Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar todos los tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar todos los popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Configuración de alertas automáticas
    var alertList = document.querySelectorAll('.alert-auto-dismiss');
    alertList.forEach(function (alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // Cerrar después de 5 segundos
    });
    
    // Validación de formularios
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
    
    // Contador para carrito de compras
    function actualizarContadorCarrito() {
        const contador = document.getElementById('cart-counter');
        if (contador) {
            fetch('/api/carrito/contador/')
                .then(response => response.json())
                .then(data => {
                    if (data.count > 0) {
                        contador.textContent = data.count;
                        contador.classList.remove('d-none');
                    } else {
                        contador.classList.add('d-none');
                    }
                })
                .catch(error => console.error('Error al actualizar contador:', error));
        }
    }
    
    // Si existe el contador del carrito, actualizarlo periódicamente
    if (document.getElementById('cart-counter')) {
        actualizarContadorCarrito();
        setInterval(actualizarContadorCarrito, 60000); // Actualizar cada minuto
    }
    
    // Funcionalidad para añadir al carrito
    const botonesAgregarCarrito = document.querySelectorAll('.btn-add-to-cart');
    botonesAgregarCarrito.forEach(boton => {
        boton.addEventListener('click', function(e) {
            e.preventDefault();
            const productoId = this.getAttribute('data-producto-id');
            const cantidad = document.querySelector(`#cantidad-${productoId}`) ? 
                             document.querySelector(`#cantidad-${productoId}`).value : 1;
            
            fetch('/api/carrito/agregar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    producto_id: productoId,
                    cantidad: cantidad
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    mostrarNotificacion('Producto añadido al carrito', 'success');
                    actualizarContadorCarrito();
                } else {
                    mostrarNotificacion(data.message || 'Error al añadir al carrito', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarNotificacion('Error al procesar la solicitud', 'danger');
            });
        });
    });
    
    // Función para mostrar notificaciones
    function mostrarNotificacion(mensaje, tipo = 'info') {
        const contenedorNotificaciones = document.getElementById('notificaciones');
        if (!contenedorNotificaciones) {
            // Crear contenedor si no existe
            const nuevoContenedor = document.createElement('div');
            nuevoContenedor.id = 'notificaciones';
            nuevoContenedor.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(nuevoContenedor);
        }
        
        const toastElement = document.createElement('div');
        toastElement.className = `toast align-items-center text-white bg-${tipo} border-0`;
        toastElement.setAttribute('role', 'alert');
        toastElement.setAttribute('aria-live', 'assertive');
        toastElement.setAttribute('aria-atomic', 'true');
        
        toastElement.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${mensaje}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        document.getElementById('notificaciones').appendChild(toastElement);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Eliminar después de mostrarse
        toastElement.addEventListener('hidden.bs.toast', function () {
            toastElement.remove();
        });
    }
    
    // Función para obtener cookies (para CSRF)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Inicialización de datepickers
    const datepickers = document.querySelectorAll('.datepicker');
    if (datepickers.length > 0) {
        datepickers.forEach(el => {
            // Aquí se puede inicializar un datepicker personalizado o usar el nativo
            el.setAttribute('type', 'date');
        });
    }
    
    // Inicialización de selectores de tiempo
    const timepickers = document.querySelectorAll('.timepicker');
    if (timepickers.length > 0) {
        timepickers.forEach(el => {
            // Aquí se puede inicializar un timepicker personalizado o usar el nativo
            el.setAttribute('type', 'time');
        });
    }
    
    // Funcionalidad para filtros de búsqueda
    const filtroForm = document.getElementById('filtro-form');
    if (filtroForm) {
        const inputsFiltro = filtroForm.querySelectorAll('input, select');
        inputsFiltro.forEach(input => {
            input.addEventListener('change', function() {
                filtroForm.submit();
            });
        });
    }
    
    // Funcionalidad para vista previa de imágenes
    const inputsImagen = document.querySelectorAll('.input-imagen-preview');
    inputsImagen.forEach(input => {
        input.addEventListener('change', function() {
            const previewElement = document.getElementById(this.getAttribute('data-preview'));
            if (previewElement && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewElement.src = e.target.result;
                    previewElement.classList.remove('d-none');
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
});

// Funcionalidad para confirmar acciones
function confirmarAccion(mensaje, callback) {
    if (confirm(mensaje)) {
        callback();
    }
}

// Funcionalidad para actualizar cantidad en carrito
function actualizarCantidadCarrito(itemId, nuevaCantidad) {
    fetch('/api/carrito/actualizar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            item_id: itemId,
            cantidad: nuevaCantidad
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar la UI
            document.getElementById(`subtotal-${itemId}`).textContent = data.subtotal;
            document.getElementById('carrito-total').textContent = data.total;
        } else {
            mostrarNotificacion(data.message || 'Error al actualizar carrito', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion('Error al procesar la solicitud', 'danger');
    });
}

// Función para eliminar item del carrito
function eliminarItemCarrito(itemId) {
    confirmarAccion('¿Está seguro de eliminar este producto del carrito?', function() {
        fetch('/api/carrito/eliminar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                item_id: itemId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Eliminar el elemento de la UI
                document.getElementById(`item-carrito-${itemId}`).remove();
                document.getElementById('carrito-total').textContent = data.total;
                
                // Si no quedan items, mostrar mensaje de carrito vacío
                if (data.items_count === 0) {
                    document.getElementById('carrito-items').innerHTML = '<div class="alert alert-info">El carrito está vacío</div>';
                    document.getElementById('carrito-acciones').classList.add('d-none');
                }
                
                actualizarContadorCarrito();
            } else {
                mostrarNotificacion(data.message || 'Error al eliminar del carrito', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al procesar la solicitud', 'danger');
        });
    });
}

// Función para reservar recurso
function reservarRecurso(recursoId) {
    const fechaInicio = document.getElementById('fecha_inicio').value;
    const fechaFin = document.getElementById('fecha_fin').value;
    const cantidad = document.getElementById('cantidad').value;
    
    if (!fechaInicio || !fechaFin) {
        mostrarNotificacion('Debe seleccionar fechas de inicio y fin', 'warning');
        return;
    }
    
    fetch('/api/alquiler/reservar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            recurso_id: recursoId,
            fecha_inicio: fechaInicio,
            fecha_fin: fechaFin,
            cantidad: cantidad
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarNotificacion('Reserva realizada con éxito', 'success');
            // Redirigir a la página de reservas
            window.location.href = '/socios/mis-reservas/';
        } else {
            mostrarNotificacion(data.message || 'Error al realizar la reserva', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion('Error al procesar la solicitud', 'danger');
    });
}

// Función para inscribirse a una clase
function inscribirseClase(sesionId) {
    fetch('/api/clases/inscribirse/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            sesion_id: sesionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarNotificacion('Inscripción realizada con éxito', 'success');
            // Actualizar UI o redirigir
            window.location.href = '/socios/mis-clases/';
        } else {
            mostrarNotificacion(data.message || 'Error al realizar la inscripción', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion('Error al procesar la solicitud', 'danger');
    });
}

// Función para cancelar inscripción a clase
function cancelarInscripcion(inscripcionId) {
    confirmarAccion('¿Está seguro de cancelar esta inscripción?', function() {
        fetch('/api/clases/cancelar-inscripcion/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                inscripcion_id: inscripcionId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarNotificacion('Inscripción cancelada con éxito', 'success');
                // Actualizar UI o redirigir
                window.location.reload();
            } else {
                mostrarNotificacion(data.message || 'Error al cancelar la inscripción', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            mostrarNotificacion('Error al procesar la solicitud', 'danger');
        });
    });
}

// Función para obtener cookies (para CSRF)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
