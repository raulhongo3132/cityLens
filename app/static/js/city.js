const API_URL = "http://localhost:5000/api";

// CITY_NAME viene inyectado por Jinja2 en city.html
// Si por algún motivo no existe, cae al query param como respaldo
let currentCity = (typeof CITY_NAME !== 'undefined' && CITY_NAME)
    ? CITY_NAME
    : new URLSearchParams(window.location.search).get('name') || "Paris";

document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) lucide.createIcons();
    document.getElementById('city-title').innerText = currentCity;

    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDarkMode = document.documentElement.classList.contains('dark') || prefersDark;

    if (isDarkMode) document.documentElement.classList.add('dark');
    actualizarBotonModo(isDarkMode);

    switchCategory('familiar');
});

function toggleDarkMode() {
    const isDark = document.documentElement.classList.toggle('dark');
    actualizarBotonModo(isDark);
}

function actualizarBotonModo(isDark) {
    const btn = document.getElementById('theme-toggle-btn');
    document.documentElement.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');

    if (btn) {
        const iconName = isDark ? 'sun' : 'moon';
        const text = isDark ? 'Modo Claro' : 'Modo Oscuro';
        btn.innerHTML = `<i data-lucide="${iconName}" class="w-4 h-4"></i> ${text}`;
        if (window.lucide) lucide.createIcons();
    }
}

function switchCategory(cat) {
    const categories = ['familiar', 'gastronomico', 'nocturna', 'alternativo'];

    categories.forEach(c => {
        const btn = document.getElementById(`btn-${c}`);
        if (btn) {
            const isActive = c === cat;
            btn.classList.toggle('active', isActive);
            btn.classList.toggle('bg-brand', isActive);
            btn.classList.toggle('text-white', isActive);
            btn.classList.toggle('bg-transparent', !isActive);
        }
    });

    const list = document.getElementById('places-list');
    list.innerHTML = `
        <div class="text-center py-10 opacity-50 flex flex-col items-center">
            <i data-lucide="loader-2" class="w-8 h-8 animate-spin text-brand mb-3"></i>
            <p class="text-xs font-black force-black m-0 tracking-widest uppercase">Localizando...</p>
        </div>`;
    if (window.lucide) lucide.createIcons();

    fetchPlaces(currentCity, cat);
}

async function fetchPlaces(city, category) {
    try {
        const res = await fetch(`${API_URL}/places?city=${encodeURIComponent(city)}&category=${encodeURIComponent(category)}`);
        const data = await res.json();
        if (!res.ok) throw new Error();
        renderPlaces(data.places || []);
    } catch {
        setTimeout(() => renderPlaces(generateMocks(city, category)), 600);
    }
}

function renderPlaces(places) {
    const list = document.getElementById('places-list');
    const map = document.getElementById('map');
    const placeholder = document.getElementById('map-placeholder');

    if (map) map.classList.replace('opacity-0', 'opacity-100');
    if (placeholder) placeholder.classList.add('opacity-0');

    if (places.length === 0) {
        list.innerHTML = `<p class="text-center force-black opacity-30 py-10 text-xs tracking-widest uppercase">Sin resultados disponibles</p>`;
        return;
    }

    list.innerHTML = `
        <div class="flex flex-col gap-4 pb-10">
            ${places.map((p, i) => `
                <div class="card-lista-lugar p-4 animate-fade-in" style="animation-delay: ${i * 0.05}s">
                    <div class="flex items-center justify-between mb-3 gap-3">
                        <h4 class="m-0 font-serif text-2xl fw-bold force-black truncate">${p.nombre}</h4>
                        <div class="text-amber-400 text-xl flex-shrink-0">
                            ${'★'.repeat(Math.round(p.rating))}${'☆'.repeat(5 - Math.round(p.rating))}
                        </div>
                    </div>
                    <div class="card-texto text-sm space-y-1 opacity-80">
                        <p class="m-0 flex items-center gap-2">
                            <i data-lucide="map-pin" class="w-4 h-4 force-black"></i>
                            <span class="force-black">${p.direccion}</span>
                        </p>
                        <p class="m-0 flex items-center gap-2">
                            <i data-lucide="clock" class="w-4 h-4 force-black"></i>
                            <span class="force-black">${p.horarios}</span>
                        </p>
                    </div>
                </div>
            `).join('')}
        </div>`;

    if (window.lucide) lucide.createIcons();
}

function generateMocks(city, cat) {
    const prefixes = {
        familiar: ['Parque', 'Museo', 'Zoológico', 'Plaza'],
        gastronomico: ['Restaurante', 'Bistró', 'Mercado', 'Café'],
        nocturna: ['Club', 'Bar', 'Terraza', 'Pub'],
        alternativo: ['Galería', 'Bazar', 'Foro', 'Estudio']
    };

    return Array.from({ length: 4 }, (_, i) => ({
        nombre: `${prefixes[cat][i % 4]} ${city} ${i + 1}`,
        rating: 4.5,
        direccion: `Calle Principal #${100 + i * 10}, Centro`,
        horarios: cat === 'nocturna' ? "19:00 - 02:00" : "09:00 - 21:00"
    }));
}
