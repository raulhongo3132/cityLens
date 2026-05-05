const API_URL = `${window.location.origin}/api`;

/**
 * 🛡️ IDENTIDAD ANÓNIMA (Persistencia Momento A -> Momento B)
 * Generamos un UUID único para este navegador si no existe.
 * Esto permite que los favoritos se asocien a este dispositivo en la DB.
 */
const USER_UUID = (() => {
    let uuid = localStorage.getItem("citylens_uuid");
    if (!uuid) {
        uuid = crypto.randomUUID();
        localStorage.setItem("citylens_uuid", uuid);
    }
    return uuid;
})();

document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) lucide.createIcons();

    // Configuración inicial de modo oscuro
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const currentTheme = document.documentElement.classList.contains("dark") || prefersDark;
    
    if (currentTheme) document.documentElement.classList.add("dark");
    actualizarBotonModo(currentTheme);

    // Carga inicial de favoritos desde la Base de Datos
    cargarFavoritos();
});

function toggleDarkMode() {
    const isDark = document.documentElement.classList.toggle("dark");
    actualizarBotonModo(isDark);
}

function actualizarBotonModo(isDark) {
    const btn = document.getElementById("theme-toggle-btn");
    document.documentElement.setAttribute("data-bs-theme", isDark ? "dark" : "light");

    if (btn) {
        const iconName = isDark ? "sun" : "moon";
        const text = isDark ? "Modo Claro" : "Modo Oscuro";
        btn.innerHTML = `<i data-lucide="${iconName}" class="w-4 h-4"></i> ${text}`;
        if (window.lucide) lucide.createIcons();
    }
}

function switchTab(tab) {
    const tabs = ["explorar", "favoritos", "nosotros"];
    const activeClasses = "cat-btn px-6 md:px-8 py-3 text-[14px] md:text-[18px] font-black tracking-[0.2em] uppercase transition-all duration-300 bg-[#27dae0] text-white shadow-md border-0";
    const inactiveClasses = "cat-btn px-6 md:px-8 py-3 text-[14px] md:text-[18px] font-black tracking-[0.2em] uppercase transition-all duration-300 bg-transparent hover:text-[#27dae0] dark:hover:text-[#27dae0] shadow-none border-0 force-black";

    tabs.forEach((t) => {
        const section = document.getElementById(`section-${t}`);
        const btn = document.getElementById(`tab-${t}`);
        if (section) section.classList.toggle("d-none", tab !== t);
        if (btn) btn.className = tab === t ? activeClasses : inactiveClasses;
    });

    if (tab === "favoritos") cargarFavoritos();
}

function handleSearch(e) {
    if (e.key === "Enter") buscarCiudad();
}

async function buscarCiudad() {
    const inputField = document.getElementById("search-input");
    const btn = document.getElementById("search-btn");
    const container = document.getElementById("search-result-container");
    const query = inputField.value.trim();

    if (!query || query.length < 2) {
        showToast("Por favor ingresa una ciudad válida", "error");
        return;
    }

    btn.disabled = true;
    const originalBtnText = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Buscando...';
    
    try {
        const res = await fetch(`${API_URL}/city?name=${encodeURIComponent(query)}`);
        const data = await res.json();

        if (!res.ok) throw new Error(data.error || "Ciudad no encontrada");

        const cityData = {
            ciudad: data.name || query,
            pais: data.country || "Desconocido",
            poblacion: data.population ? data.population.toLocaleString() : "N/A",
            zonaHoraria: data.timezone || "N/A",
        };

        container.innerHTML = renderTicket(cityData);
        if (window.lucide) lucide.createIcons();
        showToast(`¡Destino localizado: ${cityData.ciudad}!`);
    } catch (err) {
        container.innerHTML = `
            <div class="mt-8 p-10 card-lugar shadow-xl rounded-sm text-center animate-fade-in border-t-[6px] border-red-500">
                <i data-lucide="map-x" class="w-12 h-12 mx-auto mb-4 text-red-500"></i>
                <h3 class="text-3xl font-serif text-red-500 mb-2">Destino no encontrado</h3>
                <p class="text-[12px] font-sans-ui card-texto uppercase tracking-widest m-0 opacity-70">Verifica la ortografía o conexión.</p>
            </div>`;
        showToast(err.message, "error");
        if (window.lucide) lucide.createIcons();
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalBtnText;
        if (window.lucide) lucide.createIcons();
    }
}

function renderTicket(data) {
    const campos = [
        { l: "PAÍS", v: data.pais, i: "flag" },
        { l: "POBLACIÓN", v: data.poblacion, i: "users" },
        { l: "HUSO HORARIO", v: data.zonaHoraria, i: "clock" },
    ];

    return `
        <div class="mt-8 w-full card-lugar shadow-2xl relative animate-fade-in border-t-[6px] border-[#27dae0] rounded-sm">
            <div class="p-8 md:p-12">
                <div class="mb-8 border-b border-[#27dae0] pb-6">
                    <span class="text-[12px] md:text-[14px] font-black tracking-[0.3em] text-[#27dae0] uppercase">Destino Localizado</span>
                    <h2 class="text-6xl md:text-7xl font-serif mt-2 leading-none card-texto capitalize m-0">${data.ciudad}</h2>
                </div>
                <div class="row g-4 font-sans-ui mb-10">
                    ${campos.map(item => `
                        <div class="col-12 col-md-4">
                            <div class="p-6 md:p-8 card-info shadow-sm flex flex-col justify-center h-full rounded-sm">
                                <p class="text-[12px] md:text-[13px] font-black text-[#27dae0] uppercase tracking-widest flex items-center gap-2 m-0 mb-3">
                                    <i data-lucide="${item.i}" class="w-4 h-4"></i> ${item.l}
                                </p>
                                <p class="text-2xl font-bold leading-tight card-texto m-0">${item.v}</p>
                            </div>
                        </div>`).join("")}
                </div>
                <div class="d-flex flex-column flex-sm-row gap-3 w-100 font-sans-ui">
                    <a href="/city?name=${encodeURIComponent(data.ciudad)}" class="flex-1 text-center px-4 py-3 text-[14px] md:text-[16px] font-black tracking-widest bg-[#27dae0] text-white shadow-md hover:bg-[#1cb0b5] uppercase transition-all text-decoration-none border-0 rounded-sm">
                        ¡Explorar en City Lens!
                    </a>
                    <button onclick="guardarFavorito('${data.ciudad}')" class="flex-1 text-center px-4 py-3 text-[14px] md:text-[16px] font-black tracking-widest bg-[#27dae0] text-white shadow-md hover:bg-[#1cb0b5] uppercase transition-all border-0 rounded-sm">
                        ¡Añadir a Favoritos!
                    </button>
               </div>
            </div>
        </div>`;
}

/**
 * ⭐ NUEVA FUNCIÓN: Guarda el favorito en el Backend (Persistencia Real)
 * Envía el nombre de la ciudad y el UUID del navegador.
 */
async function guardarFavorito(nombre) {
    try {
        const res = await fetch(`${API_URL}/favorites`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                city_name: nombre,
                user_uuid: USER_UUID
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Error al guardar");

        showToast(`¡${nombre} añadido a tus favoritos!`);
        cargarFavoritos(); // Actualizamos la lista automáticamente
    } catch (err) {
        showToast(err.message, "error");
    }
}

/**
 * 🔄 NUEVA FUNCIÓN: Recupera los favoritos de la Base de Datos
 */
async function cargarFavoritos() {
    const list = document.getElementById("fav-list");
    const counter = document.getElementById("fav-counter");
    if (!list) return;

    try {
        const res = await fetch(`${API_URL}/favorites?uuid=${USER_UUID}`);
        const data = await res.json();

        if (!res.ok) throw new Error("Error al cargar favoritos");

        if (counter) counter.innerText = `${data.length} FAVORITOS`;

        if (data.length === 0) {
            list.innerHTML = `<p class="text-center py-20 opacity-50 uppercase tracking-widest text-3xl card-texto m-0 font-sans-ui">¡No hay favoritos!</p>`;
            return;
        }

        list.innerHTML = `
            <div class="row g-4">
                ${data.map(fav => `
                    <div class="col-12 col-md-6 col-lg-4">
                        <div class="card-lugar p-6 shadow-md border-t-4 border-[#27dae0] animate-fade-in rounded-sm">
                            <h4 class="text-2xl font-serif mb-2 capitalize card-texto">${fav.name}</h4>
                            <p class="text-[10px] opacity-70 uppercase tracking-widest mb-4 card-texto">${fav.country}</p>
                            <a href="/city?name=${encodeURIComponent(fav.name)}" class="text-[#27dae0] font-black text-[11px] uppercase tracking-widest hover:underline text-decoration-none">
                                Ver detalles →
                            </a>
                        </div>
                    </div>`).join('')}
            </div>`;
        if (window.lucide) lucide.createIcons();
    } catch (err) {
        list.innerHTML = `<p class="text-center py-20 text-red-500 uppercase tracking-widest text-sm">Error de conexión con el servidor</p>`;
    }
}

function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    const toast = document.createElement("div");
    const isError = type === "error";
    
    toast.className = `p-4 px-6 toast-dinamico border-l-4 ${isError ? 'border-red-500' : 'border-[#27dae0]'} shadow-2xl flex align-items-center gap-4 text-[11px] font-black uppercase tracking-widest animate-fade-in mb-3`;
    toast.innerHTML = `<i data-lucide="${isError ? 'x-circle' : 'check-circle'}" class="w-5 h-5 ${isError ? 'text-red-500' : 'text-[#27dae0]'}"></i> <span>${message}</span>`;
    
    container.appendChild(toast);
    if (window.lucide) lucide.createIcons();

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(10px)";
        toast.style.transition = "all 0.5s ease";
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}