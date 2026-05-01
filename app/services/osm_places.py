import logging
import time

import requests

from app.constants import PLACE_CATEGORIES

logger = logging.getLogger(__name__)


def fetch_places_from_wrapper(city_name, iso_code, capital, category, limit=10):
    """
    Patrón Wrapper: Se comunica con Overpass API.
    Utiliza el Índice ISO (Primary Key Global) para búsquedas instantáneas,
    evitando los escaneos masivos (Full Table Scans) causados por diferencias de idioma.
    """
    logger.info(
        f"🌐 Consultando OSM Overpass para '{category}' en {city_name} (ISO: {iso_code})..."
    )

    # 1. Mapeo de categorías con red de seguridad
    category_info = PLACE_CATEGORIES.get(category.lower())
    if not category_info:
        category_info = PLACE_CATEGORIES.get("turismo")
        logger.warning(
            f"Categoría '{category}' no encontrada, usando 'turismo' como default"
        )

    tags_list = category_info.get("osm_tags", ['["tourism"="attraction"]'])

    # 2. Construcción Dinámica de la Consulta Overpass QL
    query_body = ""
    for tag in tags_list:
        # Nodos y Vías son las estructuras más ligeras y precisas para lugares comerciales.
        query_body += f"      node{tag}['name'](area.searchArea);\n"
        query_body += f"      way{tag}['name'](area.searchArea);\n"

    # 🚀 OPTIMIZACIÓN ARQUITECTÓNICA DE GRADO COMERCIAL
    # Usamos estrictamente el Código ISO. Esto garantiza una resolución de área
    # en milisegundos, sorteando la barrera del idioma (ej. Tokyo vs 東京都).
    if iso_code:
        area_filter = f'["ISO3166-1"="{iso_code.upper()}"]'
    else:
        # Fallback de seguridad (extremadamente raro que REST Countries no dé ISO)
        area_filter = f'["admin_level"="2"]["name"="{city_name}"]'

    overpass_query = f"""
    [out:json][timeout:30];
    area{area_filter}->.searchArea;
    (
{query_body}
    );
    /* EL ORDEN ES VITAL: grado (body/tags), geometría (center), límite */
    out body center {limit};
    """

    # Usamos un endpoint alternativo de Overpass (Kumi Systems o main) más rápido.
    url = "https://overpass-api.de/api/interpreter"

    headers = {
        "User-Agent": "CityLens_Project/1.0 (Systems_Engineering_Student_Project)",
        "Accept": "application/json",
    }

    # 3. Manejo de Errores: Exponential Backoff mitigando el Rate Limit
    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
        try:
            response = requests.post(
                url, data=overpass_query.encode("utf-8"), headers=headers, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Datos obtenidos exitosamente de OpenStreetMap")
                return data

            elif response.status_code in [429, 504]:
                wait_time = base_delay * (2**attempt)
                logger.warning(
                    f"⚠️ Servidor saturado (Código {response.status_code}). "
                    f"Reintentando en {wait_time}s... (Intento {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
                continue

            else:
                logger.error(
                    f"❌ Error crítico en Overpass: Código {response.status_code}"
                )
                return None

        except requests.exceptions.Timeout:
            wait_time = base_delay * (2**attempt)
            logger.warning(
                f"⏳ Tiempo de espera agotado. Reintentando en {wait_time}s..."
            )
            time.sleep(wait_time)
            continue
        except requests.exceptions.RequestException as e:
            logger.error(f"🚨 Error de conexión grave con Overpass API: {e}")
            return None

    logger.error("❌ Se agotaron los reintentos.")
    return None
