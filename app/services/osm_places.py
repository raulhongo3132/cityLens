import logging
import time

import requests

from app.constants import PLACE_CATEGORIES

logger = logging.getLogger(__name__)


def fetch_places_from_wrapper(city_name, latitude, longitude, category, limit=10):
    """
    Patrón Wrapper: Comunica con Overpass API usando búsqueda por RADIO (around:).

    ✅ MÉTODO QUE FUNCIONA:
    - Solo funciona: around: (radio alrededor de coordenadas exactas)
    - NO funciona: area[], bbox directo

    OPTIMIZACIONES CRÍTICAS:
    - Radio: 25km (no 50km - causa timeouts de Overpass)
    - Tags limitados: Solo usa los 2 primeros tags más específicos
    - Timeout: 20s (reduce carga del servidor)
    - Query structure simplificada
    """
    logger.info(
        f"🌐 Consultando OSM Overpass para '{category}' en {city_name} "
        f"({latitude}, {longitude})..."
    )

    # Validar coordenadas
    if latitude is None or longitude is None:
        logger.error(f"Coordenadas inválidas para {city_name}")
        return None

    # 1. Mapeo de categorías
    category_info = PLACE_CATEGORIES.get(category.lower())
    if not category_info:
        category_info = PLACE_CATEGORIES.get("turismo")
        logger.warning(f"Categoría '{category}' no encontrada, usando 'turismo'")

    # 🚀 OPTIMIZACIÓN: Solo usa los primeros 2 tags más específicos
    tags_list = category_info.get("osm_tags", ['["tourism"="attraction"]'])[:2]
    logger.debug(f"Tags a consultar: {tags_list}")

    # 2. Radio optimizado: 25km (no causa timeouts)
    radius_meters = 25000

    # 3. Construcción de la query
    # IMPORTANTE: Cada etiqueta en una línea separada dentro del query
    query_body = ""
    for tag in tags_list:
        query_body += f"  node{tag}(around:{radius_meters},{latitude},{longitude});\n"

    overpass_query = f"""[out:json][timeout:20];
(
{query_body});
out body {limit};
"""

    url = "https://overpass-api.de/api/interpreter"
    headers = {
        "User-Agent": "CityLens/1.0",
        "Accept": "application/json",
    }

    logger.debug(f"Query Overpass (primeras 300 chars):\n{overpass_query[:300]}...")

    # 4. Exponential Backoff con optimización
    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
        try:
            logger.debug(f"[{attempt + 1}/{max_retries}] Enviando a Overpass...")

            response = requests.post(
                url,
                data=overpass_query.encode("utf-8"),
                headers=headers,
                timeout=25,  # Un poco más que el timeout de la query
            )

            if response.status_code == 200:
                data = response.json()

                # Detectar avisos del servidor
                if "remark" in data:
                    logger.warning(f"⚠️ Overpass: {data['remark']}")

                count = len(data.get("elements", []))
                logger.info(f"✅ {count} elementos obtenidos de OpenStreetMap")
                return data

            elif response.status_code in [429, 504]:
                wait_time = base_delay * (2**attempt)
                logger.warning(
                    f"⚠️ HTTP {response.status_code} - esperando {wait_time}s ({attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
                continue

            else:
                logger.error(f"❌ HTTP {response.status_code}: {response.text[:200]}")
                return None

        except requests.exceptions.Timeout:
            wait_time = base_delay * (2**attempt)
            logger.warning(
                f"⏳ Timeout ({attempt + 1}/{max_retries}) - esperando {wait_time}s..."
            )
            time.sleep(wait_time)
            continue

        except requests.exceptions.RequestException as e:
            logger.error(f"🚨 {type(e).__name__}: {e}")
            return None

        except ValueError as e:
            logger.error(f"🚨 JSON parsing error: {e}")
            return None

    logger.error("❌ Se agotaron los reintentos")
    return None
