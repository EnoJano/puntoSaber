/* =====================================================================
   INICIO.JS – PUNTO SABER
   Funcionalidades:
   - Acordeón
   - Buscador + filtros
   - Modal de archivos
   - Vista previa PDF
   - Calificación y comentarios
===================================================================== */

/* =====================================================================
   ACORDEÓN
===================================================================== */
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".acordeon-header").forEach(header => {
        header.addEventListener("click", () => {
            const item = header.parentElement;
            const contenido = item.querySelector(".acordeon-contenido");
            const icono = header.querySelector(".acordeon-icon");

            item.classList.toggle("abierto");

            if (item.classList.contains("abierto")) {
                contenido.style.display = "block";
                icono.textContent = "▼";
            } else {
                contenido.style.display = "none";
                icono.textContent = "▶";
            }
        });
    });
});

/* =====================================================================
   BUSCADOR Y FILTROS
===================================================================== */
const buscador = document.getElementById("buscador");
const filtros = document.querySelectorAll(".filtro");
const contador = document.getElementById("contador-resultados");
const sinResultados = document.getElementById("sin-resultados");

function obtenerFiltrosActivos() {
    return Array.from(filtros)
        .filter(f => f.checked)
        .map(f => f.value);
}

buscador.addEventListener("input", filtrarTodo);
filtros.forEach(f => f.addEventListener("change", filtrarTodo));

function limpiarResaltado(el) {
    el.innerHTML = el.textContent;
}

function resaltarTexto(el, texto) {
    if (!texto) return;
    const regex = new RegExp(`(${texto})`, "gi");
    el.innerHTML = el.textContent.replace(regex, "<mark>$1</mark>");
}

function filtrarTodo() {
    const texto = buscador.value.toLowerCase().trim();
    const palabras = texto.split(/\s+/).filter(p => p.length > 0);
    const filtrosActivos = obtenerFiltrosActivos();
    let totalResultados = 0;

    document.querySelectorAll(".seccion").forEach(seccion => {
        const idSeccion = seccion.id;

        // filtro por checkbox
        if (!filtrosActivos.includes(idSeccion)) {
            seccion.style.display = "none";
            return;
        }

        let coincidenciasSeccion = 0;

        seccion.querySelectorAll(".acordeon-item").forEach(item => {
            const titulo = item.querySelector(".acordeon-title");
            const hijos = item.querySelectorAll("li");

            limpiarResaltado(titulo);
            hijos.forEach(li => limpiarResaltado(li));

            let coincidenciasItem = 0;

            // si no hay texto, mostrar todo
            if (palabras.length === 0) {
                item.style.display = "block";
                hijos.forEach(li => li.style.display = "list-item");
                coincidenciasSeccion++;
                totalResultados += hijos.length;
                return;
            }

            // texto del título (autor / docente / categoría)
            const textoTitulo = titulo.textContent.toLowerCase();

            // ¿todas las palabras están en el título?
            const tituloCoincide = palabras.some(p =>
                textoTitulo.includes(p)
            );

            hijos.forEach(li => {
                const textoLi = li.textContent.toLowerCase();

                // ¿todas las palabras están en el item?
                const coincide = palabras.some(p =>
                    textoLi.includes(p)
                );

                if (coincide || tituloCoincide) {
                    li.style.display = "list-item";
                    palabras.forEach(p => resaltarTexto(li, p));
                    coincidenciasItem++;
                    totalResultados++;
                } else {
                    li.style.display = "none";
                }
            });

            if (tituloCoincide || coincidenciasItem > 0) {
                item.style.display = "block";

                // 🔓 ABRIR ACORDEÓN AUTOMÁTICAMENTE
                item.classList.add("abierto");

                palabras.forEach(p => resaltarTexto(titulo, p));
                coincidenciasSeccion++;
            } else {
                item.style.display = "none";

                // 🔒 CERRAR SI NO COINCIDE
                item.classList.remove("abierto");
            }
        });

        seccion.style.display = coincidenciasSeccion > 0 ? "block" : "none";
    });

    // contador
    contador.textContent = totalResultados > 0
        ? `Resultados encontrados: ${totalResultados}`
        : "";

    sinResultados.style.display =
        totalResultados === 0 && palabras.length > 0
            ? "block"
            : "none";
}

/* =====================================================================
   MODAL DE ARCHIVO
===================================================================== */
const modal = document.getElementById("modalArchivo");
const modalTitulo = document.getElementById("modalTitulo");
const modalPreview = document.getElementById("modalPreview");
const modalDescargar = document.getElementById("modalDescargar");
const cerrarModal = document.querySelector(".modal-cerrar");
const sinPreview = document.getElementById("sinPreview");

let archivoActual = null;
let calificacionSeleccionada = 0;

/* Abrir modal */
document.querySelectorAll(".archivo-item").forEach(item => {
    item.addEventListener("click", () => {
        archivoActual = item.dataset.id;

        // Reset modal
        modalTitulo.textContent = "";
        modalPreview.src = "";
        modalPreview.style.display = "none";
        modalDescargar.href = "";
        sinPreview.style.display = "none";
        document.getElementById("modalComentario").value = "";
        calificacionSeleccionada = 0;

        document.querySelectorAll(".estrellas span")
            .forEach(s => s.classList.remove("activa"));

        modal.style.display = "flex";

        fetch(`/archivo/${archivoActual}/`)
            .then(res => res.json())
            .then(data => {
                modalTitulo.textContent = data.titulo;
                modalDescargar.href = data.archivo_url;

                // Vista previa SOLO PDF
                if (data.archivo_url?.toLowerCase().endsWith(".pdf")) {
                    modalPreview.src = data.archivo_url;
                    modalPreview.style.display = "block";
                } else {
                    sinPreview.style.display = "block";
                }

                // Promedio
                document.getElementById("promedioEstrellas").textContent = data.promedio;
                document.getElementById("totalCalificaciones").textContent =
                    data.total_calificaciones;

                // Comentarios
                const lista = document.getElementById("listaComentarios");
                lista.innerHTML = "";

                data.comentarios.forEach(c => {
                    lista.innerHTML += `
                        <div class="modal-comentario-item">
                            <strong>${c.alumno}</strong> (${c.puntaje}⭐)
                            <p>${c.comentario}</p>
                        </div>
                    `;
                });

                // Mi calificación
                if (data.mi_calificacion) {
                    calificacionSeleccionada = data.mi_calificacion.puntaje;
                    document.getElementById("modalComentario").value =
                        data.mi_calificacion.comentario;

                    document.querySelectorAll(".estrellas span").forEach(s => {
                        if (s.dataset.valor <= calificacionSeleccionada) {
                            s.classList.add("activa");
                        }
                    });
                }
            });
    });
});

/* Cerrar modal */
cerrarModal.addEventListener("click", () => {
    modal.style.display = "none";
    modalPreview.src = "";
    sinPreview.style.display = "none";
});

/* =====================================================================
   ESTRELLAS
===================================================================== */
document.querySelectorAll(".estrellas span").forEach(estrella => {
    estrella.addEventListener("click", () => {
        calificacionSeleccionada = estrella.dataset.valor;

        document.querySelectorAll(".estrellas span").forEach(s => {
            s.classList.toggle("activa", s.dataset.valor <= calificacionSeleccionada);
        });
    });
});

/* =====================================================================
   GUARDAR CALIFICACIÓN
===================================================================== */
document.getElementById("guardarCalificacion").addEventListener("click", () => {
    const comentario = document.getElementById("modalComentario").value;

    if (!calificacionSeleccionada) {
        alert("Debes seleccionar una calificación");
        return;
    }

    fetch("/calificar/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({
            archivo_id: archivoActual,
            puntaje: calificacionSeleccionada,
            comentario
        })
    })
        .then(res => res.json())
        .then(data => {
            alert(data.mensaje);
            modal.style.display = "none";
        })
        .catch(() => {
            alert("Error al guardar la calificación");
        });
});