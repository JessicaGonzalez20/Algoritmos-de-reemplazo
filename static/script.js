document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM completamente cargado");

    const preloader = document.querySelector(".wheel-and-hamster");
    const content = document.querySelector(".contenido");

    if (content) {
        // Inicialmente ocultamos el contenido
        content.style.display = "none";
        content.style.opacity = "0";
    }

    // Mostramos el preloader durante 3 segundos
    setTimeout(() => {
        if (preloader) preloader.style.opacity = "0";  // Desvanecer el preloader

        // Después de medio segundo, ocultamos el preloader y mostramos el contenido
        setTimeout(() => {
            if (preloader) preloader.style.display = "none";  // Ocultar el preloader

            if (content) {
                content.style.display = "block";  // Mostrar el contenido
                setTimeout(() => {
                    content.style.opacity = "1";  // Aplicar opacidad al contenido
                    content.classList.add("mostrar");  // Agregar clase para animación
                }, 10);
            }
        }, 500);  // Transición de desvanecimiento del preloader
    }, 2000);  // Duración del preloader

    // Manejo del formulario (Botón Simular)
    let simularBtn = document.querySelector("#simularBtn");
    if (simularBtn) {
        simularBtn.addEventListener("click", function (e) {
            e.preventDefault();
            ejecutarSimulacion();
        });
    }

    // Botón de nueva simulación
    let newSimulation = document.getElementById("newSimulation");
    if (newSimulation) {
        newSimulation.addEventListener("click", function () {
            location.reload();  // Recargar la página
        });
    }
});

// Función para ejecutar la simulación
function ejecutarSimulacion() {
    let algoritmo = document.getElementById("algorithm").value;
    let frames = parseInt(document.getElementById("frames").value);
    let sequenceInput = document.getElementById("sequence").value;
    let referencias = sequenceInput.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x));

    if (isNaN(frames) || frames < 1 || referencias.length === 0) {
        alert("Por favor, complete todos los campos correctamente.");
        return;
    }

    // Realizar la simulación (solicitud a un servidor)
    fetch("/simular", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ algoritmo, frames, sequence: referencias })
    })
    .then(response => response.json())
    .then(data => mostrarResultados(data))
    .catch(error => console.error("Error en la simulación:", error));
}

// Función para mostrar los resultados
function mostrarResultados(data) {
    document.getElementById("fallos").innerHTML = `<h3>Fallos de página: ${data.fallos}</h3>`;
    let tabla = `<table><thead><tr><th>Referencia</th>`;
    
    // Crear los encabezados de la tabla (marcos)
    for (let i = 0; i < data.frames[0].length; i++) {
        tabla += `<th>Marco ${i + 1}</th>`;
    }
    tabla += `</tr></thead><tbody>`;

    // Crear las filas de la tabla con los marcos
    data.frames.forEach((fila, i) => {
        tabla += `<tr><td>${data.referencias[i]}</td>`;
        fila.forEach(m => {
            tabla += `<td>${m === null ? '-' : m}</td>`;  // Si el marco es nulo, mostrar un guion
        });
        tabla += `</tr>`;
    });
    tabla += `</tbody></table>`;

    // Insertar la tabla de resultados
    document.getElementById("tabla-resultados").innerHTML = tabla;
}
