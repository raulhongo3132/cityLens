/**
 * test_security.js
 *
 * Ejemplos prácticos de uso de la seguridad API Key
 * Integrable en app/static/js/ para pruebas de desarrollo
 *
 * Uso:
 *   1. Copiar este archivo a app/static/js/test_security.js
 *   2. Incluir <script src="/static/js/test_security.js"></script> en base.html
 *   3. Abrir consola del navegador y ejecutar las funciones
 */

const API_URL = window.location.origin;
const API_KEY = "tu_clave_api_secreta_aqui"; // ⚠️ Cambiar por el valor en .env

/**
 * Ejemplo 1: Petición exitosa (con clave válida)
 * Ejecutar: testSuccessfulRequest()
 */
async function testSuccessfulRequest() {
  console.log("🧪 Iniciando test exitoso...");

  try {
    const response = await fetch(`${API_URL}/api/favorites`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY,
      },
      body: JSON.stringify({ city_id: 1 }),
    });

    const data = await response.json();

    console.log("📊 Status Code:", response.status);
    console.log("📋 Respuesta:", data);

    if (response.ok) {
      console.log("✅ TEST EXITOSO: Favorito creado correctamente");
    } else {
      console.error("❌ Error del servidor:", data.message);
    }
  } catch (error) {
    console.error("❌ Error de red:", error);
  }
}

/**
 * Ejemplo 2: Petición fallida (sin header)
 * Ejecutar: testMissingHeader()
 */
async function testMissingHeader() {
  console.log("🧪 Iniciando test sin header...");

  try {
    const response = await fetch(`${API_URL}/api/favorites`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // ❌ FALTA: Sin X-API-KEY
      },
      body: JSON.stringify({ city_id: 1 }),
    });

    const data = await response.json();

    console.log("📊 Status Code:", response.status);
    console.log("📋 Respuesta:", data);

    if (response.status === 401) {
      console.log("✅ TEST EXITOSO: Servidor rechazó correctamente sin header");
    } else {
      console.error("❌ Respuesta inesperada");
    }
  } catch (error) {
    console.error("❌ Error de red:", error);
  }
}

/**
 * Ejemplo 3: Petición fallida (clave inválida)
 * Ejecutar: testInvalidKey()
 */
async function testInvalidKey() {
  console.log("🧪 Iniciando test con clave inválida...");

  try {
    const response = await fetch(`${API_URL}/api/favorites`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": "clave_completamente_incorrecta",
      },
      body: JSON.stringify({ city_id: 1 }),
    });

    const data = await response.json();

    console.log("📊 Status Code:", response.status);
    console.log("📋 Respuesta:", data);

    if (response.status === 403) {
      console.log(
        "✅ TEST EXITOSO: Servidor rechazó correctamente clave inválida",
      );
    } else {
      console.error("❌ Respuesta inesperada");
    }
  } catch (error) {
    console.error("❌ Error de red:", error);
  }
}

/**
 * Ejemplo 4: Obtener favoritos (sin autenticación, es público)
 * Ejecutar: testGetFavorites()
 */
async function testGetFavorites() {
  console.log("🧪 Iniciando test GET (público)...");

  try {
    const response = await fetch(`${API_URL}/api/favorites`);
    const data = await response.json();

    console.log("📊 Status Code:", response.status);
    console.log("📋 Favoritos:", data);

    if (response.ok) {
      console.log(
        `✅ TEST EXITOSO: Se obtuvieron ${data.count} favoritos sin autenticación`,
      );
    } else {
      console.error("❌ Error al obtener favoritos");
    }
  } catch (error) {
    console.error("❌ Error de red:", error);
  }
}

/**
 * Ejemplo 5: Eliminar favorito (con clave válida)
 * Ejecutar: testDeleteFavorite(1)
 */
async function testDeleteFavorite(cityId) {
  console.log(`🧪 Iniciando test DELETE para ciudad ${cityId}...`);

  try {
    const response = await fetch(`${API_URL}/api/favorites/${cityId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY,
      },
    });

    const data = await response.json();

    console.log("📊 Status Code:", response.status);
    console.log("📋 Respuesta:", data);

    if (response.ok) {
      console.log("✅ TEST EXITOSO: Favorito eliminado correctamente");
    } else {
      console.error("❌ Error al eliminar favorito");
    }
  } catch (error) {
    console.error("❌ Error de red:", error);
  }
}

/**
 * Función reutilizable: Wrapper genérico con API Key
 * Uso: await secureRequest("/api/favorites", "POST", { city_id: 1 })
 */
async function secureRequest(endpoint, method = "GET", body = null) {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  // Añadir API Key a peticiones de escritura
  if (["POST", "PUT", "DELETE"].includes(method)) {
    options.headers["X-API-KEY"] = API_KEY;
  }

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) {
      console.error(`❌ ${response.status}: ${data.message || data.error}`);
      return { success: false, status: response.status, data };
    }

    console.log(`✅ ${method} ${endpoint} exitoso`);
    return { success: true, status: response.status, data };
  } catch (error) {
    console.error("❌ Error de red:", error);
    return { success: false, error: error.message };
  }
}

/**
 * Suite de pruebas automatizadas
 * Ejecutar: runAllTests()
 */
async function runAllTests() {
  console.log("🚀 INICIANDO SUITE DE PRUEBAS DE SEGURIDAD\n");

  console.log("\n--- Test 1: GET Favoritos (sin autenticación) ---");
  await testGetFavorites();

  console.log("\n--- Test 2: POST Favorito (con clave válida) ---");
  await testSuccessfulRequest();

  console.log("\n--- Test 3: POST Favorito (sin header) ---");
  await testMissingHeader();

  console.log("\n--- Test 4: POST Favorito (clave inválida) ---");
  await testInvalidKey();

  console.log("\n✅ SUITE DE PRUEBAS COMPLETADA");
}

// Exportar para uso global
window.securityTests = {
  testSuccessfulRequest,
  testMissingHeader,
  testInvalidKey,
  testGetFavorites,
  testDeleteFavorite,
  secureRequest,
  runAllTests,
};

console.log(
  "✨ TEST_SECURITY.JS CARGADO | Ejecuta: window.securityTests.runAllTests()",
);
