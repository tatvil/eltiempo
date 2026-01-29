// ===============================
// 1) Cargar ciudades para autocompletar
// ===============================
let ciudades = [];

async function cargarCiudades() {
    const url = "https://eltiempo-api.azurewebsites.net/api/tiempo/ciudades";
    const resp = await fetch(url);
    ciudades = await resp.json();
}

cargarCiudades();


// ===============================
// 2) Autocompletado
// ===============================
const inputCiudad = document.getElementById("ciudad");
const contenedor = document.getElementById("resultado");

inputCiudad.addEventListener("input", () => {
    const texto = inputCiudad.value.toLowerCase();

    if (texto.length === 0) {
        contenedor.innerHTML = "";
        return;
    }

    const sugerencias = ciudades.filter(c => c.toLowerCase().startsWith(texto));

    mostrarSugerencias(sugerencias);
});

function mostrarSugerencias(lista) {
    if (lista.length === 0) {
        contenedor.innerHTML = "";
        return;
    }

    let html = "<ul class='sugerencias'>";
    lista.forEach(c => {
        html += `<li onclick="seleccionarCiudad('${c}')">${c}</li>`;
    });
    html += "</ul>";

    contenedor.innerHTML = html;
}

function seleccionarCiudad(ciudad) {
    inputCiudad.value = ciudad;
    contenedor.innerHTML = "";
}


// ===============================
// 3) Funciones auxiliares
// ===============================
function formatearFecha(fechaISO) {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleDateString("es-ES");
}

function media(arr) {
    return arr.reduce((a, b) => a + b, 0) / arr.length;
}

function agruparPorDia(datos) {
    const grupos = {};

    datos.forEach(d => {
        const fecha = d.fecha.split("T")[0];

        if (!grupos[fecha]) {
            grupos[fecha] = {
                fecha: fecha,
                amanecer: d.amanecer,
                anochecer: d.anochecer,
                tempMin: [],
                tempMax: [],
                humedad: [],
                vientoVel: [],
                vientoDir: [],
                nubes: [],
                lluvia: []
            };
        }

        grupos[fecha].tempMin.push(d.temp_Min);
        grupos[fecha].tempMax.push(d.temp_Max);
        grupos[fecha].humedad.push(d.humedad);
        grupos[fecha].vientoVel.push(d.viento_Velocidad);
        grupos[fecha].vientoDir.push(d.viento_Direccion);
        grupos[fecha].nubes.push(d.nubes);
        grupos[fecha].lluvia.push(d.lluvia);
    });

    return Object.values(grupos).map(g => ({
        fecha: g.fecha,
        amanecer: g.amanecer,
        anochecer: g.anochecer,
        tempMin: media(g.tempMin),
        tempMax: media(g.tempMax),
        humedad: media(g.humedad),
        vientoVel: media(g.vientoVel),
        vientoDir: media(g.vientoDir),
        nubes: media(g.nubes),
        lluvia: media(g.lluvia)
    }));
}

function filtrarPorFecha(datos) {
    const desde = document.getElementById("fechaDesde").value;
    const hasta = document.getElementById("fechaHasta").value;

    return datos.filter(d => {
        const fecha = d.fecha;
        if (desde && fecha < desde) return false;
        if (hasta && fecha > hasta) return false;
        return true;
    });
}


// ===============================
// 4) Búsqueda al pulsar el botón
// ===============================
document.getElementById("btnBuscar").addEventListener("click", async () => {
    const ciudad = inputCiudad.value.trim();

    if (!ciudad) {
        contenedor.innerHTML = "<p>Introduce una ciudad.</p>";
        return;
    }

    const url = `https://eltiempo-api.azurewebsites.net/api/tiempo/ciudad/${ciudad}`;

    try {
        const respuesta = await fetch(url);

        if (!respuesta.ok) {
            contenedor.innerHTML = "<p>No se encontraron datos.</p>";
            return;
        }

        let datos = await respuesta.json();

        // 1) Agrupar por día
        datos = agruparPorDia(datos);

        // 2) Filtrar por fecha
        datos = filtrarPorFecha(datos);

        // 3) Construcción de la tabla
        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Amanecer</th>
                        <th>Anochecer</th>
                        <th>Temp. Min</th>
                        <th>Temp. Max</th>
                        <th>Humedad</th>
                        <th>Viento Vel.</th>
                        <th>Viento Dir.</th>
                        <th>Nubes</th>
                        <th>Lluvia</th>
                    </tr>
                </thead>
                <tbody>
        `;

        datos.forEach(d => {
            html += `
                <tr>
                    <td>${formatearFecha(d.fecha)}</td>
                    <td>${d.amanecer}</td>
                    <td>${d.anochecer}</td>
                    <td>${d.tempMin.toFixed(1)}</td>
                    <td>${d.tempMax.toFixed(1)}</td>
                    <td>${d.humedad.toFixed(1)}</td>
                    <td>${d.vientoVel.toFixed(1)}</td>
                    <td>${d.vientoDir.toFixed(1)}</td>
                    <td>${d.nubes.toFixed(1)}</td>
                    <td>${d.lluvia.toFixed(1)}</td>
                </tr>
            `;
        });

        html += "</tbody></table>";

        // 4) Medias globales
        const mediaMin = media(datos.map(d => d.tempMin));
        const mediaMax = media(datos.map(d => d.tempMax));

        html += `
            <div class="medias">
                <p><strong>Media Temp. Mínima:</strong> ${mediaMin.toFixed(1)}°C</p>
                <p><strong>Media Temp. Máxima:</strong> ${mediaMax.toFixed(1)}°C</p>
            </div>
        `;

        contenedor.innerHTML = html;

        // 5) Dibujar gráfico
        dibujarGrafico(datos);

    } catch (error) {
        contenedor.innerHTML = "<p>Error al conectar con la API.</p>";
    }
});


// ===============================
// 5) Gráfico con Chart.js
// ===============================
let grafico = null;

function dibujarGrafico(datos) {
    const ctx = document.getElementById("grafico").getContext("2d");

    const fechas = datos.map(d => formatearFecha(d.fecha));
    const tempMin = datos.map(d => d.tempMin);
    const tempMax = datos.map(d => d.tempMax);

    if (grafico) grafico.destroy();

    grafico = new Chart(ctx, {
        type: "line",
        data: {
            labels: fechas,
            datasets: [
                {
                    label: "Temp. Mínima",
                    data: tempMin,
                    borderColor: "#0054a4",
                    backgroundColor: "#a4d7f4",
                    fill: false,
                    tension: 0.2
                },
                {
                    label: "Temp. Máxima",
                    data: tempMax,
                    borderColor: "#ff9900",
                    backgroundColor: "#ffc24a",
                    fill: false,
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: true
        }
    });
}
