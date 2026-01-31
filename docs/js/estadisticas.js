const API_URL = "servidor/api-weather-reverse.php?ciudad=madrid";

/* ---------- UTILIDADES ---------- */

function $(id) {
    return document.getElementById(id);
}

function monthName(monthIndex) {
    return new Date(2026, monthIndex, 1)
        .toLocaleDateString("es-ES", { month: "long" });
}

/* ---------- CARGA PRINCIPAL ---------- */

async function loadStats() {
    try {
        const res = await fetch(API_URL);
        const data = await res.json();

        if (!data || !data.length) throw "Sin datos";

        renderLastDay(data[0]);
        renderMonthStats(data);
        renderTrend(data);

        $("stats-location").textContent = "Madrid (datos históricos)";
    } catch (e) {
        $("stats-location").textContent = "Error cargando estadísticas";
        console.error(e);
    }
}

/* ---------- ÚLTIMO DÍA ---------- */

function renderLastDay(day) {

    $("last-date").textContent = day.dia;
    $("last-temp").textContent = `${day.temp_min}°C / ${day.temp_max}°C`;
    $("last-humidity").textContent = `${Math.round(day.humedad)} %`;
    $("last-rain").textContent = `${day.lluvia} mm`;
    $("last-wind").textContent = `${Math.round(day.viento_velocidad)} km/h`;
    $("last-sunrise").textContent = day.amanecer;
    $("last-sunset").textContent = day.anochecer;

}

/* ---------- RESUMEN DEL MES ---------- */

function renderMonthStats(data) {

    const now = new Date();
    const month = now.getMonth();
    const year = now.getFullYear();


    const monthData = data.filter(d => {
        const date = new Date(d.dia);
        return date.getMonth() === month && date.getFullYear() === year;
    });

    if (!monthData.length) return;

    const maxTemps = monthData.map(d => d.temp_max);
    const minTemps = monthData.map(d => d.temp_min);

    const lluvia = monthData.reduce(
        (sum, d) => sum + parseFloat(d.lluvia), 0
    );

    const humedad = (
        monthData.reduce((sum, d) => sum + parseFloat(d.humedad), 0)
        / monthData.length
    ).toFixed(1);

    $("month-days").textContent = monthData.length;
    $("month-max").textContent = Math.max(...maxTemps) + "°C";
    $("month-min").textContent = Math.min(...minTemps) + "°C";
    $("month-rain").textContent = lluvia.toFixed(1) + " mm";
    $("month-humidity").textContent = humedad + " %";


}

/* ---------- TENDENCIA HISTÓRICA ---------- */

function renderTrend(data) {

    const now = new Date();
    const month = now.getMonth();

    const byYear = {};

    data.forEach(d => {
        const date = new Date(d.dia);

        if (date.getMonth() === month) {
            const year = date.getFullYear();

            if (!byYear[year]) {
                byYear[year] = { max: [], min: [], rain: [] };
            }

            byYear[year].max.push(d.temp_max);
            byYear[year].min.push(d.temp_min);
            byYear[year].rain.push(parseFloat(d.lluvia));
        }
    });

    const container = $("trend-container");
    container.innerHTML = "";

    Object.keys(byYear)
        .sort()
        .forEach(year => {

            const maxAvg = (
                byYear[year].max.reduce((a,b)=>a+b,0) /
                byYear[year].max.length
            ).toFixed(1);

            const minAvg = (
                byYear[year].min.reduce((a,b)=>a+b,0) /
                byYear[year].min.length
            ).toFixed(1);

            const rainTotal = (
                byYear[year].rain.reduce((a,b)=>a+b,0)
            ).toFixed(1);

            container.innerHTML += `
                <p>
                    <strong>${year}</strong> →
                    Máx ${maxAvg}°C ·
                    Mín ${minAvg}°C ·
                    Lluvia ${rainTotal} mm
                </p>
            `;
        });
}


/* ---------- INIT ---------- */

document.addEventListener("DOMContentLoaded", () => {
    $("year").textContent = new Date().getFullYear();
    loadStats();
});
