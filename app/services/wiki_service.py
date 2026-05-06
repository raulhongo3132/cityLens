import logging

import requests

logger = logging.getLogger(__name__)


def fetch_wikipedia_summary(place_name):
    """
    Wrapper para la API de Wikipedia.
    Obtiene el resumen de un lugar desde la API REST de Wikipedia en español.

    Args:
        place_name (str): Nombre del lugar a buscar.

    Returns:
        dict: Diccionario con 'description', 'extract' y 'thumbnail_source' si existe,
              o None si no se encuentra.
    """
    url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{place_name}"

    # Header requerido por Wikimedia para evitar 403 Forbidden
    headers = {"User-Agent": "Datamundi-CityLens/1.0 (estudiante@sistemas.edu)"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extraer campos relevantes
        result = {
            "description": data.get("description", ""),
            "extract": data.get("extract", ""),
            "thumbnail_source": data.get("thumbnail", {}).get("source", "")
            if data.get("thumbnail")
            else "",
        }

        logger.info(f"✅ Resumen de Wikipedia obtenido para '{place_name}'")
        return result

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"❌ Página no encontrada en Wikipedia para '{place_name}'")
            return None
        elif e.response.status_code == 403:
            logger.warning(f"❌ Acceso denegado (403) a Wikipedia para '{place_name}'")
            return None
        else:
            logger.error(
                f"🚨 Error HTTP {e.response.status_code} al consultar Wikipedia: {e}"
            )
            return None

    except requests.exceptions.Timeout:
        logger.error(f"🚨 Timeout al consultar Wikipedia para '{place_name}'")
        return None

    except requests.exceptions.ConnectionError as e:
        logger.error(f"🚨 Error de conexión con Wikipedia: {e}")
        return None

    except requests.exceptions.RequestException as e:
        logger.error(f"🚨 Error en request a Wikipedia: {e}")
        return None

    except ValueError as e:
        logger.error(f"🚨 Error al parsear JSON de Wikipedia: {e}")
        return None

    except ValueError as e:
        logger.error(f"🚨 Error al parsear JSON de Wikipedia: {e}")
        return None
