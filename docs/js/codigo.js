/* ==============================================
   FUNCIONES AUXILIARES
============================================== */

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" });
}

function formatDuration(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h}h ${m}m ${s}s`;
}

function ponerlaFechaActual() {
    const now = new Date();
    const dateString = now.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    document.getElementById("fecha-actual").textContent = dateString;
}

/* ================================
   6. SANTO DEL DÍA
================================ */

async function santoDelDia() {
    const hoy = new Date();
    const offset = hoy.getTimezoneOffset() * 60000;
    const fechaISO = new Date(hoy - offset).toISOString().split('T')[0];

    try {
        const res = await fetch('data/santos.json');
        const listaSantos = await res.json();

        const elSanto = listaSantos.find(d => d.fecha === fechaISO);

        if (elSanto) {
            document.getElementById("santo-del-dia").textContent = elSanto.santo;
            santoDelDiaElem.textContent = elSanto.santo;
            descripcionSantoDelDiaElem.textContent = elSanto.descripcion || "";
        }
    } catch (e) {
        console.error("Error en la carga de santos:", e);
    }
}

/* ==============================================
   GEOLOCALIZACIÓN CENTRAL
============================================== */
async function getLocationOnce() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) reject("Geolocalización no soportada");
        navigator.geolocation.getCurrentPosition(
            pos => resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
            err => reject(err.message)
        );
    });
}

async function getLocationName(lat, lon) {
    try {
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`;
        const res = await fetch(url);
        const data = await res.json();

        if (data.address) {
            if (data.address.city) return data.address.city + ", " + data.address.country;
            if (data.address.town) return data.address.town + ", " + data.address.country;
            if (data.address.village) return data.address.village + ", " + data.address.country;
            if (data.address.hamlet) return data.address.hamlet + ", " + data.address.country;
        }

        return "Ubicación desconocida";
    } catch {
        return "Ubicación desconocida";
    }
}

/* ==============================================
   TARJETA SOL / ANOCHECER
============================================== */
async function getSunTimes(lat, lon) {
    const url = `https://api.sunrise-sunset.org/json?lat=${lat}&lng=${lon}&formatted=0`;
    const response = await fetch(url);
    const data = await response.json();
    return data.results;
}

async function updateSunCard(lat, lon) {
    try {
        const sun = await getSunTimes(lat, lon);
        const cityName = await getLocationName(lat, lon);

        const sunrise = new Date(sun.sunrise);
        const sunset = new Date(sun.sunset);

        document.getElementById("sunrise").textContent = formatTime(sun.sunrise);
        document.getElementById("sunset").textContent = formatTime(sun.sunset);
        document.getElementById("day-length").textContent = formatDuration((sunset - sunrise)/1000);
        document.getElementById("location").textContent = cityName;

        const card = document.getElementById("sun-card");
        const sunIcon = document.getElementById("sun-icon");

        function updateMode() {
            const now = new Date();
            if (now >= sunrise && now <= sunset) {
                card.style.background = "rgba(26,26,26,0.85)";
                sunIcon.textContent = "☀️";
            } else {
                card.style.background = "rgba(10,10,30,0.85)";
                sunIcon.textContent = "🌙";
            }
        }

        function updateCountdown() {
            const now = new Date();
            let target;
            let text = "Queda ";

            if (now < sunrise) target = sunrise;
            else if (now >= sunrise && now <= sunset) target = sunset;
            else target = new Date(sunrise.getTime() + 24*60*60*1000);

            const diff = Math.floor((target - now) / 1000);
            const durationStr = formatDuration(diff);

            text += (target.getTime() === sunrise.getTime()) 
                    ? durationStr + " hasta anochecer" 
                    : durationStr + " hasta amanecer";

            document.getElementById("countdown").textContent = text;
        }

        updateMode();
        updateCountdown();
        setInterval(() => { updateMode(); updateCountdown(); }, 1000);

    } catch (err) {
        document.getElementById("location").textContent = "Error obteniendo datos: " + err.message;
    }
}

/* ==============================================
   TIEMPO ACTUAL
============================================== */
async function getWeather(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    // Open-Meteo API
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&temperature_unit=celsius&windspeed_unit=kmh&timezone=auto`;

    try {
        const res = await fetch(url);
        const data = await res.json();
        const weather = data.current_weather;

        document.getElementById("temperature").textContent = `${weather.temperature}°C`;
        document.getElementById("condition").textContent = `Viento ${weather.windspeed} km/h`;
        document.getElementById("humidity").textContent = "N/A";
        document.getElementById("wind").textContent = "N/A";

    } catch (err) {
        document.getElementById("location").textContent = "Error al obtener el tiempo";
        console.error(err);
    }
}

function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            document.getElementById("location").textContent = "Permiso denegado para obtener ubicación.";
            break;
        case error.POSITION_UNAVAILABLE:
            document.getElementById("location").textContent = "Ubicación no disponible.";
            break;
        case error.TIMEOUT:
            document.getElementById("location").textContent = "Tiempo de espera agotado.";
            break;
        default:
            document.getElementById("location").textContent = "Error desconocido.";
    }
}

/* ==============================================
   FASES LUNARES
============================================== */
function getMoonPhase() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    const day = now.getDate();

    const c = Math.floor(365.25 * year);
    const e = Math.floor(30.6 * (month + 1));
    const jd = c + e + day - 694039.09; 
    const phase = (jd / 29.53) % 1; 
    const age = phase * 29.53;

    let phaseName = "", icon = "";

    if (age < 1.84566) { phaseName = "Luna Nueva"; icon = "🌑"; }
    else if (age < 5.53699) { phaseName = "Creciente Iluminante"; icon = "🌒"; }
    else if (age < 9.22831) { phaseName = "Cuarto Creciente"; icon = "🌓"; }
    else if (age < 12.91963) { phaseName = "Gibosa Creciente"; icon = "🌔"; }
    else if (age < 16.61096) { phaseName = "Luna Llena"; icon = "🌕"; }
    else if (age < 20.30228) { phaseName = "Gibosa Menguante"; icon = "🌖"; }
    else if (age < 23.99361) { phaseName = "Cuarto Menguante"; icon = "🌗"; }
    else if (age < 27.68493) { phaseName = "Creciente Menguante"; icon = "🌘"; }
    else { phaseName = "Luna Nueva"; icon = "🌑"; }

    document.getElementById("moon-phase").textContent = phaseName;
    document.getElementById("moon-icon").textContent = icon;
}

function moonPhaseForDate(year, month, day) {
    const c = Math.floor(365.25 * year);
    const e = Math.floor(30.6 * (month + 1));
    const jd = c + e + day - 694039.09;
    const phase = (jd / 29.53) % 1;
    const age = phase * 29.53;

    if (age < 1.84566) return "🌑";
    if (age < 5.53699) return "🌒";
    if (age < 9.22831) return "🌓";
    if (age < 12.91963) return "🌔";
    if (age < 16.61096) return "🌕";
    if (age < 20.30228) return "🌖";
    if (age < 23.99361) return "🌗";
    if (age < 27.68493) return "🌘";
    return "🌑";
}

function generateMiniMoonCalendar() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    const today = now.getDate();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const container = document.getElementById("moon-mini-calendar");

    container.innerHTML = "";

    let firstDay = new Date(year, month, 1).getDay();
    firstDay = (firstDay === 0) ? 6 : firstDay - 1;

    for (let i = 0; i < firstDay; i++) {
        const empty = document.createElement("div");
        empty.classList.add("moon-day");
        empty.style.visibility = "hidden";
        container.appendChild(empty);
    }

    for (let day = 1; day <= daysInMonth; day++) {
        const icon = moonPhaseForDate(year, month + 1, day);
        const div = document.createElement("div");
        div.classList.add("moon-day");
        if (day === today) div.classList.add("moon-today");

        div.innerHTML = `<span>${day}</span><span class="moon-icon">${icon}</span>`;
        container.appendChild(div);
    }
}

/* ==============================================
   BULLET JOURNAL RESUMEN
============================================== */
function loadBulletSummary() {
    const data = JSON.parse(localStorage.getItem("journalData")) || {};
    const now = new Date();
    const month = now.getMonth();
    const year = now.getFullYear();

    let rosario = 0, caminar = 0, vitaminas = 0, agua = 0;

    for (let key in data) {
        const d = new Date(key);
        if (d.getMonth() === month && d.getFullYear() === year) {
            if(data[key].rosario) rosario++;
            if(data[key].caminar) caminar++;
            if(data[key].vitaminas) vitaminas++;
            agua += Number(data[key].agua || 0);
        }
    }

    document.getElementById("bj-rosario").textContent = rosario;
    document.getElementById("bj-caminar").textContent = caminar;
    document.getElementById("bj-vitaminas").textContent = vitaminas;
    document.getElementById("bj-agua").textContent = agua;
}

/* ==============================================
   INICIALIZACIÓN
============================================== */
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("year").innerText = new Date().getFullYear();

    ponerlaFechaActual();
    santoDelDia();
    loadBulletSummary();
    getMoonPhase();
    generateMiniMoonCalendar();

    // Inicializar sol/luna + tiempo actual con una sola geolocalización
    initApp();
});

async function initApp() {
    try {
        const { lat, lon } = await getLocationOnce();
        updateSunCard(lat, lon);
        getWeather({ coords: { latitude: lat, longitude: lon } });
    } catch (err) {
        document.getElementById("location").textContent = "Error: " + err;
    }
}
