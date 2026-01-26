// --- Funciones auxiliares ---
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

// --- Obtener datos Sunrise-Sunset API ---
async function getSunTimes(lat, lon) {
    const url = `https://api.sunrise-sunset.org/json?lat=${lat}&lng=${lon}&formatted=0`;
    const response = await fetch(url);
    const data = await response.json();
    return data.results;
}

// --- Obtener nombre de ciudad ---
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

// --- Detectar ubicación actual ---
function getLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) reject("Geolocalización no soportada");
        navigator.geolocation.getCurrentPosition(
            pos => resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
            err => reject(err.message)
        );
    });
}

// --- Actualizar tarjeta ---
async function updateSunCard(lat, lon) {
    try {
        const sun = await getSunTimes(lat, lon);
        const cityName = await getLocationName(lat, lon);

        const sunrise = new Date(sun.sunrise);
        const sunset = new Date(sun.sunset);
        const now = new Date();

        document.getElementById("sunrise").textContent = formatTime(sun.sunrise);
        document.getElementById("sunset").textContent = formatTime(sun.sunset);
        document.getElementById("day-length").textContent = formatDuration((sunset - sunrise)/1000);
        document.getElementById("location").textContent = cityName;

        const card = document.getElementById("sun-card");
        const sunIcon = document.getElementById("sun-icon");

        function updateMode() {
            const now = new Date();
            if (now >= sunrise && now <= sunset) {
                card.style.transition = "background 1s ease";
                card.style.background = "rgba(26,26,26,0.85)";
                sunIcon.textContent = "☀️";
            } else {
                card.style.transition = "background 1s ease";
                card.style.background = "rgba(10,10,30,0.85)";
                sunIcon.textContent = "🌙";
            }
        }

        function updateCountdown() {
            const now = new Date();
            let target, text;

            text = "Queda ";

            if (now < sunrise) { // antes del amanecer
                target = sunrise;
            } else if (now >= sunrise && now <= sunset) { // durante el día
                target = sunset;
            } else { // después del anochecer
                target = new Date(sunrise.getTime() + 24*60*60*1000); // siguiente amanecer
            }

            const diff = Math.floor((target - now) / 1000); // calcular diferencia en segundos
            const durationStr = formatDuration(diff);

            // Añadir texto específico según el objetivo
            if (target.getTime() === sunrise.getTime()) {
                text += durationStr + " hasta anochecer";
            } else {
                text += durationStr + " hasta amancer";
            }

            document.getElementById("countdown").textContent = text;
    }


        updateMode();
        updateCountdown();
        setInterval(() => { updateMode(); updateCountdown(); }, 1000);

    } catch (err) {
        document.getElementById("location").textContent = "Error obteniendo datos: " + err.message;
    }
}

// --- Inicialización ---
async function initSunCard() {
    try {
        const { lat, lon } = await getLocation();
        updateSunCard(lat, lon);
    } catch (err) {
        document.getElementById("location").textContent = "Error: " + err;
    }
}

// --- Ejecutar ---
initSunCard();
