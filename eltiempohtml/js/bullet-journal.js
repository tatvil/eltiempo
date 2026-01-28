let currentDate = new Date();
const fields = ['rosario', 'vitaminas', 'caminar', 'agua', 'mood'];

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    setupAutoSave();
    updateUI();
});

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function updateUI() {
    const dateString = currentDate.toLocaleDateString('es-ES', {
        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
    });
    document.getElementById('currentDateDisplay').innerText = dateString;
    
    loadDayData();
    updateExtras();
}

function changeDay(offset) {
    currentDate.setDate(currentDate.getDate() + offset);
    updateUI();
}

/* STORAGE */
function loadDayData() {
    const data = JSON.parse(localStorage.getItem('journalData')) || {};
    const day = data[formatDate(currentDate)] || {};
    
    fields.forEach(f => {
        const el = document.getElementById(f);
        if (el.type === 'checkbox') el.checked = day[f] || false;
        else el.value = day[f] || '';
    });
}

function setupAutoSave() {
    fields.forEach(f => {
        document.getElementById(f).addEventListener('change', () => {
            const data = JSON.parse(localStorage.getItem('journalData')) || {};
            const key = formatDate(currentDate);
            if (!data[key]) data[key] = {};
            
            fields.forEach(field => {
                const el = document.getElementById(field);
                data[key][field] = el.type === 'checkbox' ? el.checked : el.value;
            });
            localStorage.setItem('journalData', JSON.stringify(data));
        });
    });
}

/* EXTRAS: SANTORAL Y CUMPLES */
async function updateExtras() {
    const iso = formatDate(currentDate);
    // Santoral
    try {
        const resS = await fetch('data/santos.json');
        const santos = await resS.json();
        const s = santos.find(x => x.fecha === iso);
        document.getElementById('saintDisplay').innerText = s ? `Santo: ${s.santo}` : "Santoral";
        document.getElementById('santodeldia').innerText = s ? `Santo del día: ${s.santo}` : "Santo del día desconocido";
    } catch (e) { console.log("Falta santos.json"); }

    // Cumples
    try {
        const resC = await fetch('data/cumples.json');
        const cumples = await resC.json();
        const c = cumples.find(x => x.fecha === iso.slice(5));
        document.getElementById('cumpleDisplay').innerText = c ? `🎂 ${c.persona}` : "";
    } catch (e) { }
}

/* IMPRESIÓN MENSUAL A5 */
async function printFullMonth() {
    const data = JSON.parse(localStorage.getItem('journalData')) || {};
    const month = currentDate.getMonth();
    const year = currentDate.getFullYear();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    let html = "";
    for (let i = 1; i <= daysInMonth; i++) {
        const date = new Date(year, month, i);
        const key = formatDate(date);
        const dayData = data[key] || {};
        
        html += `
            <div class="page-a5">
                <h1> ${date.toLocaleDateString('es-ES',{weekday:'long'})}, ${i} ${date.toLocaleDateString('es-ES',{month:'long'})} de ${date.getFullYear()}</h1>
                <div id="santodeldia">Santo del dia</div>
                <p style="margin-top:10px">
                    Rosario: ${dayData.rosario ? '✔' : '☐'} | Pasos: ${dayData.caminar || 0}
                    | Vitaminas: ${dayData.vitaminas ? '✔' : '☐'} | Agua: ${dayData.agua || 0}ml
                </p>
                <div class="dots-bg"></div>
            </div>
        `;
    }
    
    document.getElementById('printArea').innerHTML = html;
    window.print();
}

function resetData() {
    if(confirm("¿Seguro que quieres borrar todo el historial?")) {
        localStorage.clear();
        location.reload();
    }
}