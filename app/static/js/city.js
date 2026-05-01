const API_URL = `${window.location.origin}/api`;

// CITY_NAME viene inyectado por Jinja2 en city.html
// Si por algún motivo no existe, cae al query param como respaldo
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

  // Categoría por defecto alineada a la macro-escala nacional
  switchCategory("turismo");
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

function switchCategory(cat) {
  // ALL_CATEGORIES se inyecta desde el Backend vía Jinja2
  const categories = ALL_CATEGORIES;

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
    const res = await fetch(
      `${API_URL}/places?city=${encodeURIComponent(city)}&category=${encodeURIComponent(category)}`,
    );
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Error al obtener lugares");

    renderPlaces(data || [], city);
  } catch (error) {
    console.error("Error conectando con El Mesero:", error);
    const list = document.getElementById("places-list");
    list.innerHTML = `<p class="text-center force-black text-red-500 py-10 text-xs tracking-widest uppercase"><i data-lucide="alert-triangle" class="w-6 h-6 mx-auto mb-2"></i> ${error.message}</p>`;
    if (window.lucide) lucide.createIcons();
  }
}

function renderPlaces(places, cityName) {
  const list = document.getElementById("places-list");
  const map = document.getElementById("map");
  const placeholder = document.getElementById("map-placeholder");

  if (map) {
    map.classList.replace("opacity-0", "opacity-100");
    const iframe = map.querySelector("iframe");
    if (iframe) {
      // Vista Nacional por defecto con "country" para prevenir ambigüedades en Google Maps (Z=5)
      iframe.src = `https://maps.google.com/maps?q=${encodeURIComponent(cityName + " country")}&t=&z=5&ie=UTF8&iwloc=&output=embed`;
    }
  }

  if (placeholder) placeholder.classList.add("opacity-0");

  if (!Array.isArray(places) || places.length === 0) {
    list.innerHTML = `<p class="text-center force-black opacity-30 py-10 text-xs tracking-widest uppercase">Sin resultados disponibles en la base de datos</p>`;
    return;
  }

  list.innerHTML = `
        <div class="flex flex-col gap-4 pb-10">
            ${places
              .map((p, i) => {
                const safeName = encodeURIComponent(p.name || "Lugar");

                // Renderizado Condicional: Solo muestra los íconos si La Despensa tiene la información
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
                     onclick="actualizarMapa(${p.lat || null}, ${p.lon || null}, '${safeName}')">
                    
                    <div class="flex items-center justify-between mb-3 gap-3">
                        <h4 class="m-0 font-serif text-2xl fw-bold force-black truncate">${p.name || "Sin nombre"}</h4>
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
                </div>
                `;
              })
              .join("")}
        </div>`;

  if (window.lucide) lucide.createIcons();
}

// NUEVA FUNCIÓN: Mover el iframe hacia las coordenadas exactas permitiendo interacción directa
window.actualizarMapa = function (lat, lon, placeName) {
  const mapDiv = document.getElementById("map");
  const iframe = mapDiv ? mapDiv.querySelector("iframe") : null;

  if (iframe && lat && lon) {
    // Usamos las coordenadas puras. Esto permite que el botón nativo de Google Maps
    // funcione correctamente y abra la ubicación real en otra pestaña.
    iframe.src = `https://maps.google.com/maps?q=${lat},${lon}&t=&z=17&ie=UTF8&iwloc=&output=embed`;
  } else {
    console.warn("⚠️ Este lugar carece de coordenadas en la base de datos.");
  }
};
