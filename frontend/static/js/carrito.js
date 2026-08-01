// static/js/carrito.js

document.addEventListener("DOMContentLoaded", () => {
    // 1. MANTENER TU CÓDIGO ORIGINAL[cite: 6]
    // Actualizar cantidad en el carrito[cite: 6]
    const cantidadInputs = document.querySelectorAll(".form-cantidad input");[cite: 6]

    cantidadInputs.forEach(input => {[cite: 6]
        input.addEventListener("change", (e) => {[cite: 6]
            if (parseInt(e.target.value) < 1) {[cite: 6]
                e.target.value = 1;[cite: 6]
            }[cite: 6]
        });[cite: 6]
    });[cite: 6]

    // Confirmación al vaciar carrito[cite: 6]
    const vaciarBtn = document.querySelector(".btn-secundario");[cite: 6]
    if (vaciarBtn) {[cite: 6]
        vaciarBtn.addEventListener("click", (e) => {[cite: 6]
            if (!confirm("¿Seguro que querés vaciar el carrito?")) {[cite: 6]
                e.preventDefault();[cite: 6]
            } else {
                // Si acepta, vaciamos mediante la API
                e.preventDefault();
                vaciarCarritoAPI();
            }
        });[cite: 6]
    }
});

// ────────────────────────────────────────────────────────
// 2. NUEVAS FUNCIONES PARA CONECTAR CON LA API (FETCH)
// ────────────────────────────────────────────────────────

// Función para agregar un producto al carrito sin recargar la página
async function agregarAlCarrito(productoId, cantidad = 1) {
    try {
        const respuesta = await fetch(`/api/carrito/agregar/${productoId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ cantidad: cantidad })
        });
        
        if (respuesta.ok) {
            alert("¡Producto agregado al carrito, gato!");
            // Acá podés actualizar dinámicamente un contador en el header si querés
        } else {
            console.error("Error al agregar al carrito");
        }
    } catch (error) {
        console.error("Error de red:", error);
    }
}

// Función para quitar un producto del carrito
async function quitarDelCarrito(productoId) {
    try {
        const respuesta = await fetch(`/api/carrito/quitar/${productoId}`, {
            method: "DELETE"
        });
        
        if (respuesta.ok) {
            // Recargamos la vista del carrito para actualizar los totales
            location.reload();
        } else {
            console.error("Error al quitar el producto");
        }
    } catch (error) {
        console.error("Error de red:", error);
    }
}

// Función para vaciar todo el carrito desde la API
async function vaciarCarritoAPI() {
    try {
        const respuesta = await fetch("/api/carrito/vaciar", {
            method: "POST"
        });
        
        if (respuesta.ok) {
            location.reload();
        } else {
            console.error("Error al vaciar el carrito");
        }
    } catch (error) {
        console.error("Error de red:", error);
    }
}