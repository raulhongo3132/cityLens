const API_URL = `${window.location.origin}/api`;

// 🛡️ EL SEMÁFORO: Variable de estado para controlar la concurrencia
let isFetching = false;

// CITY_NAME viene inyectado por Jinja2 en city.html
let currentCity =
  typeof CITY_NAME !== "undefined" && CITY_NAME
    ? CITY_NAME
    : new URLSearchParams(window.location.search).get("name") || "Paris";

document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) lucide.createIcons();
  document.getElementById("city-title").innerText = currentCity;

  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const isDarkMode =
    document.documentElement.classList.contains("dark") || prefersDark;

  if (isDarkMode) document.documentElement.classList.add("dark");
  actualizarBotonModo(isDarkMode);

  // 1. Arquitectura Resiliente: Inicializamos el mapa independientemente de los lugares
  inicializarMapaNacional(currentCity);

  // 2. 🚀 Carga Inicial Óptima: Servimos el "Menú Degustación" por defecto
  switchCategory("destacados");
});

function toggleDarkMode() {
  const isDark = document.documentElement.classList.toggle("dark");
  actualizarBotonModo(isDark);
}

function actualizarBotonModo(isDark) {
  const btn = document.getElementById("theme-toggle-btn");
  document.documentElement.setAttribute(
    "data-bs-theme",
    isDark ? "dark" : "light",
  );

  if (btn) {
    const iconName = isDark ? "sun" : "moon";
    const text = isDark ? "Modo Claro" : "Modo Oscuro";
    btn.innerHTML = `<i data-lucide="${iconName}" class="w-4 h-4"></i> ${text}`;
    if (window.lucide) lucide.createIcons();
  }
}

// Separa el mapa para que no dependa de si "El Mesero" encuentra lugares o no
function inicializarMapaNacional(cityName) {
  const map = document.getElementById("map");
  const placeholder = document.getElementById("map-placeholder");

  if (map) {
    map.classList.replace("opacity-0", "opacity-100");
    const iframe = map.querySelector("iframe");
    if (iframe) {
      iframe.src = `https://maps.google.com/maps?q=${encodeURIComponent(cityName + " country")}&t=&z=5&ie=UTF8&iwloc=&output=embed`;
    }
  }

  if (placeholder) placeholder.classList.add("opacity-0");
}

function switchCategory(cat) {
  // 🛡️ CONTROL DE CONCURRENCIA: Si "El Mesero" ya está ocupado, ignoramos el clic
  if (isFetching) {
    console.warn("Búsqueda en progreso. Por favor, espera a que termine.");
    // Si tienes showToast disponible globalmente, puedes descomentar la siguiente línea:
    // if (typeof showToast === "function") showToast("Por favor, espera a que termine la búsqueda actual", "info");
    return;
  }

  const categories =
    typeof ALL_CATEGORIES !== "undefined"
      ? ALL_CATEGORIES
      : ["destacados", "turismo", "naturaleza", "cultura", "historico"];

  categories.forEach((c) => {
    const btn = document.getElementById(`btn-${c}`);
    if (btn) {
      const isActive = c === cat;
      btn.classList.toggle("active", isActive);
      btn.classList.toggle("bg-brand", isActive);
      btn.classList.toggle("text-white", isActive);
      btn.classList.toggle("bg-transparent", !isActive);
    }
  });

  const list = document.getElementById("places-list");

  // Mostramos el spinner de carga
  list.innerHTML = `
        <div class="text-center py-10 opacity-50 flex flex-col items-center">
            <i data-lucide="loader-2" class="w-8 h-8 animate-spin text-brand mb-3"></i>
            <p class="text-xs font-black force-black m-0 tracking-widest uppercase">Localizando...</p>
        </div>`;
  if (window.lucide) lucide.createIcons();

  fetchPlaces(currentCity, cat);
}

async function fetchPlaces(city, category) {
  const list = document.getElementById("places-list");

  // 🛡️ Cerramos el candado: Iniciamos la petición
  isFetching = true;

  try {
    const res = await fetch(
      `${API_URL}/places?city=${encodeURIComponent(city)}&category=${encodeURIComponent(category)}`,
    );

    const data = await res.json();

    // Manejo Pacífico: "El Mesero" trajo un error controlado (ej. 404 de lugares vacíos)
    if (!res.ok) {
      throw new Error(
        data.error || "No hay resultados disponibles en esta categoría.",
      );
    }

    renderPlaces(data || []);
  } catch (error) {
    console.warn("Aviso del sistema:", error.message);

    // Destruimos el spinner y mostramos la excusa elegantemente
    list.innerHTML = `
        <div class="text-center p-6 border border-[#27dae0]/30 rounded-sm bg-gray-50 dark:bg-gray-800/50">
            <i data-lucide="alert-circle" class="w-8 h-8 mx-auto mb-3 text-gray-400"></i>
            <p class="force-black text-sm tracking-widest uppercase opacity-70 m-0">${error.message}</p>
        </div>`;
    if (window.lucide) lucide.createIcons();
  } finally {
    // 🛡️ Abrimos el candado: Finaliza la ejecución sin importar si hubo éxito o error
    isFetching = false;
  }
}

async function loadPlaceDetails(placeName, detailsContainer) {
  // Mostrar spinner
  detailsContainer.classList.remove('hidden');
  detailsContainer.innerHTML = `
    <div class="text-center py-2">
      <i data-lucide="loader-2" class="w-4 h-4 animate-spin text-brand inline-block"></i>
      <span class="text-xs ml-2">Cargando detalles...</span>
    </div>
  `;
  if (window.lucide) lucide.createIcons();

  try {
    const res = await fetch(`${API_URL}/places/details?name=${encodeURIComponent(placeName)}`);
    const data = await res.json();

    if (res.ok) {
      // Inyectar imagen y texto
      let html = `<div class="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded">`;
      if (data.thumbnail_source) {
        html += `<img src="${data.thumbnail_source}" alt="${placeName}" class="w-full h-32 object-cover rounded mb-2">`;
      }
      html += `<p class="text-sm text-gray-700 dark:text-gray-300">${data.extract || data.description || 'Sin descripción disponible'}</p>`;
      html += `</div>`;
      detailsContainer.innerHTML = html;
    } else {
      detailsContainer.innerHTML = `<p class="text-sm text-gray-500 mt-2">Detalles no disponibles</p>`;
    }
  } catch (error) {
    console.error('Error cargando detalles:', error);
    detailsContainer.innerHTML = `<p class="text-sm text-red-500 mt-2">Error al cargar detalles</p>`;
  }
}

function renderPlaces(places) {
  const list = document.getElementById("places-list");

  if (!Array.isArray(places) || places.length === 0) {
    list.innerHTML = `<p class="text-center force-black opacity-30 py-10 text-xs tracking-widest uppercase">Sin resultados disponibles en la base de datos</p>`;
    return;
  }

  list.innerHTML = `
        <div class="flex flex-col gap-4 pb-10">
            ${places
              .map((p, i) => {
                const safeName = encodeURIComponent(p.name || "Lugar");

                const phoneHtml = p.phone
                  ? `<p class="m-0 flex items-center gap-2"><i data-lucide="phone" class="w-4 h-4 force-black"></i> <span class="force-black">${p.phone}</span></p>`
                  : "";
                const hoursHtml = p.opening_hours
                  ? `<p class="m-0 flex items-center gap-2"><i data-lucide="clock" class="w-4 h-4 force-black"></i> <span class="force-black">${p.opening_hours}</span></p>`
                  : "";
                const webHtml = p.website
                  ? `<p class="m-0 flex items-center gap-2"><i data-lucide="globe" class="w-4 h-4 force-black"></i> <a href="${p.website}" target="_blank" onclick="event.stopPropagation();" class="text-brand hover:underline force-black break-all">Sitio Web</a></p>`
                  : "";

                return `
                <div class="card-lista-lugar p-4 animate-fade-in cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" 
                     style="animation-delay: ${i * 0.05}s"
                     onclick="actualizarMapa(${p.lat || null}, ${p.lon || null})">
                    
                    <div class="flex items-center justify-between mb-3 gap-3">
                        <h4 class="m-0 font-serif text-2xl fw-bold force-black truncate">${p.name || "Sin nombre"}</h4>
                        <button class="btn-ver-mas bg-brand text-white px-3 py-1 rounded text-sm hover:bg-brand-dark transition-colors" data-place-name="${encodeURIComponent(p.name || "Lugar")}">
                            Ver más
                        </button>
                    </div>
                    
                    <div class="card-texto text-sm space-y-2 opacity-80">
                        <p class="m-0 flex items-center gap-2">
                            <i data-lucide="map-pin" class="w-4 h-4 force-black"></i>
                            <span class="force-black">${p.address || "Dirección no disponible"}</span>
                        </p>
                        ${phoneHtml}
                        ${hoursHtml}
                        ${webHtml}
                        <p class="m-0 flex items-center gap-2 text-xs opacity-50 pt-2 border-t border-gray-200 dark:border-gray-700">
                            <i data-lucide="tag" class="w-4 h-4 force-black"></i>
                            <span class="force-black capitalize">${p.category || "General"}</span>
                        </p>
                    </div>
                    
                    <div id="details-${i}" class="details-container mt-3 hidden">
                        <!-- Detalles de Wikipedia se inyectarán aquí -->
                    </div>
                </div>
                `;
              })
              .join("")}
        </div>`;

  if (window.lucide) lucide.createIcons();

  // Event listener para botones "Ver más" usando event delegation
  list.addEventListener('click', function(event) {
    if (event.target.classList.contains('btn-ver-mas')) {
      event.stopPropagation(); // Evitar que se active el onclick de la card
      const placeName = decodeURIComponent(event.target.getAttribute('data-place-name'));
      const detailsContainer = event.target.closest('.card-lista-lugar').querySelector('.details-container');
      loadPlaceDetails(placeName, detailsContainer);
    }
  });
}

// Permite interacción directa abriendo en la misma vista las coordenadas
window.actualizarMapa = function (lat, lon) {
  const mapDiv = document.getElementById("map");
  const iframe = mapDiv ? mapDiv.querySelector("iframe") : null;

  if (iframe && lat && lon) {
    iframe.src = `https://maps.google.com/maps?q=${lat},${lon}&t=&z=17&ie=UTF8&iwloc=&output=embed`;
  }
};
