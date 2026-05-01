# services/city_service.py
import logging
import unicodedata

import requests
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import City

logger = logging.getLogger(__name__)


def sanitize_search_term(term):
    """
    Data Cleaning de Entrada: Estandariza la entrada del usuario.
    Convierte 'MéxIcO ' en 'mexico' para evitar duplicados en BD
    y mitigar riesgos de inyección en las consultas ILIKE.
    """
    if not term:
        return ""
    # Elimina espacios extra, quita acentos y pasa a minúsculas
    term = (
        unicodedata.normalize("NFKD", term.strip())
        .encode("ASCII", "ignore")
        .decode("utf-8")
    )
    return term.lower()


def get_city_data(name):
    """
    Patrón Wrapper: Obtiene datos del país/ciudad desde caché o REST Countries.
    """
    clean_name = sanitize_search_term(name)

    if not clean_name:
        logger.warning(f"Término de búsqueda inválido: '{name}'")
        return {"error": "Término de búsqueda inválido."}, 400

    try:
        # 1. Búsqueda estandarizada en caché
        cached_city = City.query.filter(City.name.ilike(f"%{clean_name}%")).first()
        if cached_city:
            logger.info(
                f"✅ Destino '{cached_city.name}' obtenido de caché (PostgreSQL)"
            )
            return {
                "name": cached_city.name,
                "country": cached_city.country,
                "population": cached_city.population,
                "timezone": cached_city.timezone,
            }
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error de base de datos al buscar ciudad: {str(e)}")
        return {"error": "Error de base de datos.", "detalle": str(e)}, 500

    logger.info(
        f"🌐 '{name}' no encontrado en caché. Consultando REST Countries API..."
    )

    # REST Countries Endpoint
    url = f"https://restcountries.com/v3.1/translation/{name}"

    try:
        response = requests.get(url, timeout=5)
        # Fallback si no encuentra por traducción, intentar por capital
        if response.status_code == 404:
            url_capital = f"https://restcountries.com/v3.1/capital/{name}"
            response = requests.get(url_capital, timeout=5)

        response.raise_for_status()
        payload = response.json()

        if not payload:
            logger.warning(f"País no encontrado en REST Countries: {name}")
            return {"error": "No se encontraron datos."}, 404
        payload.sort(key=lambda x: x.get("population", 0), reverse=True)
        country_data = payload[0]

        # Mapeo de datos oficiales de la API
        capital_name = country_data.get("capital", [name])[0]
        country_name = country_data.get("name", {}).get("common", "Unknown")
        population = country_data.get("population", 0)

        timezones = country_data.get("timezones", ["UTC"])
        timezone_str = timezones[0] if timezones else "UTC"

        iso_code = country_data.get("cca2", "")
        flag_url = country_data.get("flags", {}).get("svg", "")

        # Obtener lat y lon
        latlng = country_data.get("latlng", [None, None])
        lat = latlng[0] if len(latlng) > 0 else None
        lon = latlng[1] if len(latlng) > 1 else None

        # 2. Persistencia Segura
        new_city = City(
            name=country_name,
            country=country_name,
            population=population,
            timezone=timezone_str,
            iso_code=iso_code,
            flag_url=flag_url,
            capital=capital_name,
            lat=lat,
            lon=lon,
        )

        db.session.add(new_city)
        db.session.commit()
        logger.info(f"✅ País '{country_name}' guardado en caché")

        return {
            "name": new_city.name,
            "country": new_city.country,
            "population": new_city.population,
            "timezone": new_city.timezone,
        }

    except requests.RequestException as e:
        db.session.rollback()
        logger.error(f"Error conectando con REST Countries API: {str(e)}")
        return {"error": "API externa no disponible.", "detalle": str(e)}, 503
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error guardando ciudad en BD: {str(e)}")
        return {"error": "Error guardando en base de datos.", "detalle": str(e)}, 500
