import logging
import time

import requests

logger = logging.getLogger(__name__)

# Mapeo de categorías con filtros por popularidad usando wikidata
OSM_CATEGORIES = {
    "gastronomico": [
        '["amenity"="restaurant"]["wikidata"]',
        '["amenity"="cafe"]["wikidata"]',
    ],
    "naturaleza": [
        '["leisure"="park"]["wikidata"]',
        '["natural"="water"]["wikidata"]',
    ],
    "cultura": [
        '["tourism"="museum"]["wikidata"]',
        '["tourism"="gallery"]["wikidata"]',
    ],
    "destacados": [
        '["tourism"="attraction"]["wikidata"]',
        '["historic"="monument"]["wikidata"]',
        '["historic"="building"]["wikidata"]',
    ],
    "turismo": [
        '["tourism"="attraction"]["wikidata"]',
        '["tourism"="viewpoint"]["wikidata"]',
        '["tourism"="theme_park"]["wikidata"]',
    ],
    "historico": [
        '["historic"="monument"]["wikidata"]',
        '["historic"="castle"]["wikidata"]',
        '["historic"="ruins"]["wikidata"]',
    ],
}


def fetch_places_from_wrapper(
    city_name, latitude, longitude, category, limit=15, bbox=None
):
    """
    Wrapper optimizado para Overpass API.

    ✅ OPTIMIZACIONES:
    - Usa nw (Node + Way) para capturar puntos y polígonos
    - Filtra por popularidad con wikidata
    - Radio: 3km (3000m) para evitar timeouts
    - Timeout: 15s en servidor
    - out center tags: extrae coordenadas de polígonos correctamente

    Args:
        city_name: Nombre de la ciudad/país
        latitude: Latitud del centroide
        longitude: Longitud del centroide
        category: Categoría de lugares
        limit: Número máximo de resultados
        bbox: Bounding box opcional [south, north, west, east]

    Returns:
        dict: JSON de Overpass API con elementos o None
    """
    logger.info(
        f"🌐 Consultando Overpass para '{category}' en {city_name} "
        f"({latitude}, {longitude})..."
    )

    # Validar coordenadas
    if latitude is None or longitude is None:
        logger.error(f"Coordenadas inválidas para {city_name}")
        return None

    # 1. Obtener etiquetas de la categoría
    etiquetas = OSM_CATEGORIES.get(
        category.lower(),
        ['["tourism"="attraction"]["wikidata"]'],
    )
    logger.debug(f"Etiquetas a consultar ({len(etiquetas)}): {etiquetas}")

    # 2. Construir consulta dinámica con nw (node + way)
    nw_query = ""
    for etiqueta in etiquetas:
        if bbox and len(bbox) == 4:
            # Usar bbox para países
            south, north, west, east = bbox
            nw_query += f"  nw({south},{west},{north},{east}){etiqueta};\n"
        else:
            # Usar around para ciudades (3km para evitar timeouts)
            nw_query += f"  nw(around:3000,{latitude},{longitude}){etiqueta};\n"

    # 3. Ensamblar query final con out center tags
    overpass_query = f"""[out:json][timeout:15];
(
{nw_query}
);
out {limit} center tags;
"""

    logger.debug(f"Query Overpass:\n{overpass_query[:300]}...")

    # 4. Headers estrictamente especificados
    url = "https://overpass-api.de/api/interpreter"
    headers = {
        "User-Agent": "Datamundi-CityLens/1.0 (estudiante@sistemas.edu)",
        "Accept": "*/*",
    }

    # 5. Exponential Backoff con reintentos
    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
        try:
            logger.debug(f"[{attempt + 1}/{max_retries}] Enviando a Overpass...")

            response = requests.post(
                url,
                data=overpass_query.encode("utf-8"),
                headers=headers,
                timeout=20,  # Timeout de cliente > timeout de servidor
            )

            # Manejo de códigos HTTP
            if response.status_code == 200:
                data = response.json()

                # Avisos del servidor
                if "remark" in data:
                    logger.warning(f"⚠️ Overpass: {data['remark']}")

                count = len(data.get("elements", []))
                logger.info(f"✅ {count} elementos obtenidos")
                return data

            elif response.status_code == 429:
                # Rate limiting
                wait_time = base_delay * (2**attempt)
                logger.warning(
                    f"⚠️ Rate limit (429) - esperando {wait_time}s "
                    f"({attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
                continue

            elif response.status_code == 504:
                # Gateway timeout
                wait_time = base_delay * (2**attempt)
                logger.warning(
                    f"⚠️ Gateway timeout (504) - esperando {wait_time}s "
                    f"({attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
                continue

            else:
                logger.error(f"❌ HTTP {response.status_code}: {response.text[:200]}")
                return None

        except requests.exceptions.Timeout:
            # Timeout en cliente
            wait_time = base_delay * (2**attempt)
            logger.warning(
                f"⏳ Timeout en cliente ({attempt + 1}/{max_retries}) "
                f"- esperando {wait_time}s..."
            )
            time.sleep(wait_time)
            continue

        except requests.exceptions.ConnectionError as e:
            logger.error(f"🚨 Error de conexión: {e}")
            return None

        except requests.exceptions.HTTPError as e:
            logger.error(f"🚨 Error HTTP: {e}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"🚨 {type(e).__name__}: {e}")
            return None

        except ValueError as e:
            logger.error(f"🚨 JSON parsing error: {e}")
            return None

    logger.error("❌ Se agotaron los reintentos (3/3)")
    return None


def extract_place_coordinates(element):
    """
    Extrae coordenadas de un elemento OSM.

    Maneja dos casos:
    - Nodos: tienen lat/lon directo
    - Polígonos (Ways/Relations): tienen lat/lon en center

    Args:
        element: Elemento OSM del JSON de Overpass

    Returns:
        tuple: (lat, lon) o (None, None) si no hay coordenadas
    """
    # Intenta primero coordinate directas (nodos)
    lat = element.get("lat")
    lon = element.get("lon")

    # Si no existen, intenta center (para polígonos)
    if lat is None or lon is None:
        center = element.get("center", {})
        lat = center.get("lat")
        lon = center.get("lon")

    return lat, lon


def extract_place_name(element):
    """
    Extrae nombre limpio de un elemento OSM.

    Args:
        element: Elemento OSM del JSON

    Returns:
        str: Nombre o 'Sin nombre'
    """
    tags = element.get("tags", {})
    return tags.get("name", "Sin nombre")


def extract_place_address(element):
    """
    Extrae dirección de tags OSM.

    Args:
        element: Elemento OSM del JSON

    Returns:
        str: Dirección o 'Dirección no disponible'
    """
    tags = element.get("tags", {})
    return tags.get("addr:street", "Dirección no disponible")


def extract_place_website(element):
    """
    Extrae website de tags OSM.

    Args:
        element: Elemento OSM del JSON

    Returns:
        str o None: URL del website si existe
    """
    tags = element.get("tags", {})
    return tags.get("website") or tags.get("contact:website")


def extract_place_phone(element):
    """
    Extrae teléfono de tags OSM.

    Args:
        element: Elemento OSM del JSON

    Returns:
        str o None: Número telefónico si existe
    """
    tags = element.get("tags", {})
    return tags.get("phone") or tags.get("contact:phone")


def extract_place_opening_hours(element):
    """
    Extrae horario de tags OSM.

    Args:
        element: Elemento OSM del JSON

    Returns:
        str o None: Horario si existe
    """
    tags = element.get("tags", {})
    return tags.get("opening_hours")
