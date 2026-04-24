const API_URL = "http://localhost:5000/api";


document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) lucide.createIcons();
    
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDark && !document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.add('dark');
        actualizarBotonModo(true);
    } else {
        actualizarBotonModo(document.documentElement.classList.contains('dark'));
    }
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

function switchTab(tab) {
    const tabs = ['explorar', 'favoritos', 'nosotros'];
    
    const activeClasses = "cat-btn px-6 md:px-8 py-3 text-[14px] md:text-[18px] font-black tracking-[0.2em] uppercase transition-all duration-300 bg-[#27dae0] text-white shadow-md border-0";
    const inactiveClasses = "cat-btn px-6 md:px-8 py-3 text-[14px] md:text-[18px] font-black tracking-[0.2em] uppercase transition-all duration-300 bg-transparent hover:text-[#27dae0] dark:hover:text-[#27dae0] shadow-none border-0 force-black";

    tabs.forEach(t => {
        const section = document.getElementById(`section-${t}`);
        const btn = document.getElementById(`tab-${t}`);
        
        if (section) {
            if (tab === t) {
                section.classList.remove('d-none');
            } else {
                section.classList.add('d-none');
            }
        }
        
        if (btn) {
            btn.className = (tab === t) ? activeClasses : inactiveClasses;
        }
    });

    if (tab === 'favoritos') cargarFavoritos();
}

function handleSearch(e) {
    if (e.key === 'Enter') buscarCiudad();
}

async function buscarCiudad() {
    const inputField = document.getElementById('search-input');
    const btn = document.getElementById('search-btn');
    const container = document.getElementById('search-result-container');
    const query = inputField.value.trim();

    if (!query || query.length < 2) {
        showToast("Por favor ingresa una ciudad válida", "error");
        return;
    }

    btn.disabled = true;
    const originalBtnText = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Buscando...';
    btn.classList.add('opacity-70', 'cursor-not-allowed');
    if (window.lucide) lucide.createIcons();
    
    container.innerHTML = '';

    try {
        const res = await fetch(`${API_URL}/city?name=${encodeURIComponent(query)}`);
        const data = await res.json();
        
        if (!res.ok) throw new Error(data.error || "Ciudad no encontrada");

        const cityData = {
            ciudad: data.name || query,
            pais: data.country || "Desconocido",
            poblacion: data.population ? data.population.toLocaleString() : "N/A",
            zonaHoraria: data.timezone || "N/A"
        };

        container.innerHTML = renderTicket(cityData);
        if (window.lucide) lucide.createIcons();
        showToast(`¡Destino localizado: ${cityData.ciudad}!`);

    } catch (err) {
        await new Promise(resolve => setTimeout(resolve, 800)); 
        
        if (query.toLowerCase() === "xyzxyz") {
            container.innerHTML = `
                <div class="mt-8 p-10 card-lugar shadow-xl rounded-sm text-center animate-fade-in border-t-[6px]" style="border-top-color: #ef4444 !important; border-color: #ef4444;">
                    <i data-lucide="map-x" class="w-12 h-12 mx-auto mb-4 text-[#ef4444]"></i>
                    <h3 class="text-3xl font-serif text-[#ef4444] mb-2">Destino no encontrado</h3>
                    <p class="text-[12px] font-sans-ui card-texto uppercase tracking-widest m-0">Verifica la ortografía.</p>
                </div>
            `;
            showToast("Error en la búsqueda", "error");
        } else {
            const isParis = query.toLowerCase() === "paris";
            const cityDataMock = {
                ciudad: query,
                pais: isParis ? "Francia" : "País Simulado",
                poblacion: isParis ? "2,161,000" : "1,500,000",
                zonaHoraria: isParis ? "CET (UTC+1)" : "UTC-5"
            };
            container.innerHTML = renderTicket(cityDataMock);
            showToast(`¡Destino localizado (Modo Prueba): ${cityDataMock.ciudad}!`);
        }
        if (window.lucide) lucide.createIcons();
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalBtnText;
        btn.classList.remove('opacity-70', 'cursor-not-allowed');
        if (window.lucide) lucide.createIcons();
    }
}

function renderTicket(data) {
    const campos = [
        { l: 'PAÍS', v: data.pais, i: 'flag' },
        { l: 'POBLACIÓN', v: data.poblacion, i: 'users' },
        { l: 'HUSO HORARIO', v: data.zonaHoraria, i: 'clock' }
    ];

    return `
        <div class="mt-8 w-full card-lugar shadow-2xl relative animate-fade-in border-t-[6px] border-t-[#27dae0] rounded-sm">
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
                        </div>
                    `).join('')}
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
        </div>
    `;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    const borderColor = type === 'error' ? 'border-[#ef4444]' : 'border-[#27dae0]';
    const textColor = type === 'error' ? 'text-[#ef4444]' : 'text-[#27dae0]';
    const iconName = type === 'error' ? 'x-circle' : 'check-circle';
    
    toast.className = `p-4 px-6 toast-dinamico border-l-4 ${borderColor} shadow-2xl flex align-items-center gap-4 text-[11px] font-black uppercase tracking-widest animate-fade-in`;
    toast.innerHTML = `<i data-lucide="${iconName}" class="w-5 h-5 ${textColor}"></i> <span>${message}</span>`;
    container.appendChild(toast);
    if (window.lucide) lucide.createIcons();
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.5s ease';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

function guardarFavorito(nombre) {
    showToast(`¡${nombre} añadido a su favoritos!`);
}

function cargarFavoritos() {
    const list = document.getElementById('fav-list');
    document.getElementById('fav-counter').innerText = `0 FAVORITOS`;
    list.innerHTML = `<p class="text-center py-20 opacity-50 uppercase tracking-widest text-3xl card-texto m-0 font-sans-ui">¡No hay favoritos!</p>`;
}