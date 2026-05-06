# Datamundi / CityLens - Documentación Técnica

## Resumen Ejecutivo

CityLens es una aplicación web diseñada para explorar y conocer ciudades a través de una interfaz de búsqueda y mapas. Su objetivo principal es ofrecer a los usuarios una experiencia de descubrimiento geográfico con datos enriquecidos de ciudades y lugares de interés, apoyándose en PostgreSQL como caché local, APIs externas para datos oficiales y búsquedas espaciales georreferenciadas.

El proyecto busca consolidar:

- una capa backend basada en Flask,
- una capa de persistencia confiable con PostgreSQL,
- una integración limpia con APIs externas (REST Countries y Overpass),
- un frontend ligero que minimiza la sobrecarga de llamadas y reduce errores de rate limiting.

## Stack Tecnológico

- Python 3.x
- Flask 3.1.x
- Flask-SQLAlchemy 3.1.x
- Flask-Migrate 4.0.x
- Flask-CORS 6.0.x
- PostgreSQL (La Despensa) con `psycopg2-binary`
- SQLAlchemy 2.x
- Requests 2.x
- Jinja2
- HTML + CSS + Bootstrap 5 + Tailwind CDN
- JavaScript Vanilla para control de estado, UI y llamadas a la API
- APIs externas:
  - OpenStreetMap Overpass API
  - REST Countries API
  - (Preparado para Google Places API según variable `GOOGLE_PLACES_KEY` en `.env.example`)

## Arquitectura y Patrones

### Patrón Wrapper para aislamiento de APIs

El proyecto aplica un patrón de wrapper en los servicios para encapsular las llamadas a APIs externas y evitar fugas de lógica en las rutas:

- `app.services.city_service.get_city_data` actúa como wrapper para REST Countries. Su responsabilidad es:
  - normalizar el término de búsqueda,
  - validar y limpiar la entrada,
  - consultar primero la caché local de PostgreSQL,
  - solicitar datos externos solo cuando es estrictamente necesario.

- `app.services.osm_places.fetch_places_from_wrapper` actúa como wrapper para Overpass API. Su responsabilidad es:
  - construir consultas espaciales de manera controlada,
  - aplicar timeout y reintentos con backoff exponencial,
  - manejar estados HTTP críticos como `429` y `504`.

Esta separación mantiene las rutas (`app.routes.cities`, `app.routes.places`) limpias y delega la complejidad de las integraciones externas al dominio de servicios.

### Data Cleaning estricto en los servicios

El proyecto implementa limpieza de datos en varios puntos clave:

- en `app.services.city_service.sanitize_search_term`, la entrada de usuario se normaliza, se elimina acentos y se convierte a minúsculas.
- en `app.routes.places.places_endpoint`, `category` se limpia con `.lower().strip()` y se valida contra `ALL_CATEGORIES`.
- en `app.services.places_service.get_places`, los resultados de Overpass se depuran:
  - se ignoran elementos sin nombre,
  - se construyen direcciones desde etiquetas `addr:street` y `addr:housenumber`,
  - se usan `tags` alternativos para website y teléfono,
  - se truncan campos a los tamaños seguros del modelo SQL.

Esto evita inyecciones, inconsistencia de datos y entradas inválidas en la base de datos.

### Control de concurrencia en el Frontend

El frontend protege la experiencia de usuario y reduce el riesgo de errores de rate limiting:

- `app/static/js/city.js` usa la variable global `isFetching` como semáforo para bloquear múltiples solicitudes simultáneas del mismo usuario.
- cuando el usuario selecciona una categoría, la aplicación no dispara una segunda petición si ya hay una en curso.
- este mecanismo previene sobredemanda en el backend y en el Overpass API, reduciendo exponencialmente las posibilidades de recibir HTTP `429`.

Aunque no existe un `debounce()` formal en el código actual, la estrategia de control de concurrencia funciona como un guardia de acceso que evita tráfico repetido.

### Seguridad con API Key (Firmas Digitales)

Se ha implementado un decorador `@require_api_key` para proteger rutas de escritura:

- `app/security.py` contiene el decorador que intercepta peticiones y valida el header `X-API-KEY`,
- compara el valor contra la variable de entorno `API_SECRET_KEY`,
- retorna HTTP 401 (Unauthorized) si el header falta,
- retorna HTTP 403 (Forbidden) si el valor no coincide,
- implementa logging estructurado para auditoría de intentos fallidos.

Las rutas seguras están en `app/routes/favorites.py`:

- `POST /api/favorites` → requiere `X-API-KEY`
- `DELETE /api/favorites/<city_id>` → requiere `X-API-KEY`
- Los endpoints `GET` son públicos (sin autenticación) para acceso libre a datos.

## Estructura del Proyecto

```text
cityLens/
├── app/
│   ├── __init__.py          # App factory y singleton DB/Migrate para inicializar Flask y PostgreSQL
│   ├── constants.py         # Categorías OSM definidas y configuración de tags de búsqueda
│   ├── models.py            # Modelos SQLAlchemy City y Place para persistencia y caché
│   ├── security.py          # Decorador @require_api_key para proteger rutas sensibles
│   ├── routes/
│   │   ├── __init__.py      # Paquete de blueprints para habilitar imports desde app.routes
│   │   ├── main.py          # Renderiza las páginas `index` y `city`
│   │   ├── cities.py        # API `/api/city`, validación y delegación al servicio de ciudades
│   │   ├── places.py        # API `/api/places`, validación de categoría y limpieza de parámetros
│   │   └── favorites.py     # API `/api/favorites` con rutas protegidas POST/DELETE y públicas GET
│   ├── services/
│   │   ├── __init__.py      # Paquete de servicios, punto de consolidación del dominio
│   │   ├── city_service.py  # Wrapper REST Countries + caché en PostgreSQL
│   │   ├── places_service.py # Lógica de búsqueda, caché, limpieza y persistencia de lugares
│   │   └── osm_places.py    # Wrapper Overpass API con reintentos y query espacial
│   ├── static/
│   │   ├── css/
│   │   │   └── global.css   # Estilos globales compartidos y overrides visuales
│   │   └── js/
│   │       ├── inicio.js    # Interacción de búsqueda inicial y favoritos UI estático
│   │       └── city.js      # Manejo del mapa, categorías y control de concurrencia
│   └── templates/
│       ├── base.html        # Layout principal con Bootstrap/Tailwind y scripts comunes
│       ├── index.html       # Página principal de búsqueda de ciudades
│       └── city.html        # Vista de detalles de ciudad con mapa y selección de categorías
├── .env.example             # Plantilla de variables de entorno, sin credenciales reales
├── .gitignore               # Exclusiones de archivos sensibles y del entorno local
├── FEATURES.md              # Documentación de funcionalidades planificadas
├── README.md                # Guía de uso rápida y puesta en marcha
├── requirements.txt         # Dependencias Python fijadas en versiones exactas
├── run.py                   # Punto de entrada de la aplicación Flask en desarrollo
├── migrations/              # Migraciones Alembic/Flask-Migrate del esquema de BD
├── test_osm.py              # Script de prueba para validar el comportamiento de Overpass
├── osm_evidencia.json       # Evidencia de consulta OSM/Overpass para auditoría
├── project_analysis.md      # Análisis del proyecto y decisiones estratégicas
├── tree.txt                 # Árbol de carpetas del proyecto
└── venv/                    # Entorno virtual local (no debe versionarse)
```

## Flujo de Datos (Data Flow)

1. El usuario inicia desde el navegador en `index.html` o `city.html`.
2. El frontend invoca el endpoint Flask:
   - `app/static/js/inicio.js` llama a `/api/city?name=...` para localizar la ciudad.
   - `app/static/js/city.js` llama a `/api/places?city=...&category=...` para obtener lugares.
3. Las rutas Flask en `app.routes.cities` y `app.routes.places` validan y limpian parámetros.
4. El servicio de ciudad en `app.services.city_service` realiza:
   - una búsqueda en PostgreSQL (`cities`),
   - si existe, devuelve la caché directamente,
   - si no existe, consulta REST Countries,
   - transforma y normaliza el JSON externo,
   - almacena la entidad `City` en la base de datos.
5. El servicio de lugares en `app.services.places_service` realiza:
   - búsqueda de ciudad en PostgreSQL por nombre o capital,
   - si la ciudad no existe, la crea con `city_service`,
   - revisión de caché en la tabla `places`,
   - si hay resultados almacenados, regresa la lista desde la base de datos.
6. Si no hay caché, el servicio construye una consulta espacial y llama a `fetch_places_from_wrapper`.
7. `app.services.osm_places` genera una consulta Overpass basada en un radio alrededor de las coordenadas de la ciudad.
   - la implementación actual usa un radio de 25 km para robustez,
   - la arquitectura está lista para adaptarse a un radio de 5 km en consultas espaciales,
   - la consulta se envía con timeout, headers y reintentos para reducir fallas de rate limiting.
8. La respuesta de Overpass se limpia, se normaliza y se persiste en PostgreSQL en `places`.
9. El backend devuelve JSON al frontend.
10. El frontend renderiza la lista de lugares, actualiza el iframe del mapa y mantiene la UI responsiva.

## Matriz de Pruebas y Certificación (Crucial)

| Criterio             | Objetivo de validación                                                                                                               | Estado esperado / Nota                                                                                     |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| Smoke Testing        | El servicio Flask arranca y los contenedores de la app y PostgreSQL quedan en estado `Up`                                            | `docker-compose up` debería mostrar ambos servicios listos y sin reinicios constantes                      |
| Connectivity Testing | Los endpoints `/api/city` y `/api/places` devuelven JSON válido sin errores desde el backend                                         | Respuesta HTTP 200 y payload JSON parseable                                                                |
| Integration Testing  | El navegador carga `city.html` y no reporta errores CORS al solicitar `/api/city` o `/api/places` desde el mismo dominio configurado | `flask-cors` debe permitir orígenes definidos en `.env` sin errores de políticas cross-origin              |
| Database Persistence | Los datos almacenados en PostgreSQL sobreviven a un reinicio del servicio gracias a volúmenes Docker                                 | El volumen del contenedor PostgreSQL debe conservar `cities` y `places` tras `docker-compose restart`      |
| Security             | No hay credenciales quemadas en código fuente y la configuración sensible se gestiona mediante `.env`                                | `.env.example` contiene plantilla; `.env` local no debe versionarse ni exponer `DATABASE_URL` o `API keys` |

## Roadmap y Tareas Pendientes

### Deudas técnicas

- Implementar persistencia de favoritos mediante un modelo `Favorite` o tabla intermedia para vincular usuarios/ciudades.
- Revisar la estrategia de radio espacial: parametrizar `radius_meters` para soportar rádius de 5 km / 10 km con criterios de precisión.
- Añadir validaciones y esquemas de respuesta estrictos para los payloads de `REST Countries` y `Overpass`.
- Mejorar el manejo de reintentos y backoff en `fetch_places_from_wrapper` para soportar `429` de forma determinista.
- Añadir pruebas automatizadas que cubran tarifas límites y fallas de API externas.
- Implementar `debouncing` real en el frontend de búsqueda de ciudad para evitar recargas repetidas al escribir.
- Añadir logging estructurado adicional para correlacionar request/response en entornos de producción.
- **✅ Implementado:** Seguridad con API Key mediante decorador `@require_api_key` para proteger rutas POST/DELETE.
- Siguiente paso en seguridad: Implementar rate limiting en el decorador para prevenir fuerza bruta.

### Fase Actual

- ✅ Implementación de capa de seguridad con decorador `@require_api_key` para proteger rutas de escritura.
- ✅ Creación de endpoints REST para gestión de favoritos (`/api/favorites`) con autenticación.
- 🔧 Integración del frontend con solicitudes autenticadas usando header `X-API-KEY`.
- 🔧 Crear modelos adicionales para persistencia real de favoritos con relaciones usuario-ciudad.
- 🔧 Escribir pruebas unitarias con pytest para validar el decorador y las rutas protegidas.

### Fase Siguiente

- Congelar dependencias en `requirements.txt` mediante `pip freeze` y validar compatibilidad.
- Crear los manifiestos `Dockerfile` y `docker-compose.yml` para orquestar:
  - aplicación Flask,
  - PostgreSQL con volumen persistente,
  - variables de entorno y configuración de red.
- Validar en Docker Compose que los favoritos persisten tras reiniciar el contenedor de PostgreSQL.

---

## Seguridad: Documentación Detallada

Para información exhaustiva sobre la implementación de API Key y seguridad de rutas, consulta [`IMPLEMENTATION_REPORT.md`](IMPLEMENTATION_REPORT.md).

---

> Nota: La aplicación ya contiene la base de la arquitectura Flask + PostgreSQL, wrappers de API, y seguridad con API Key. El siguiente paso estratégico es convertirla en un servicio orquestado con Docker Compose y cerrar la brecha de favoritos persistentes con modelo de usuario.
