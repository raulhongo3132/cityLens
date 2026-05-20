# app/services/city_service.py
import logging
import unicodedata
import requests
import os
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import City, Favorite

logger = logging.getLogger(__name__)

# ✅ Variable de entorno con fallback seguro
BASE_URL = os.getenv("RESTCOUNTRIES_API_URL", "https://restcountries.com/v3.1")


def get_city_coordinates(city_name, country_name=None):
    """
    Geocoding: Obtiene coordenadas y bbox de una ciudad/país usando Nominatim.
    """
    query = city_name
    if country_name:
        query += f", {country_name}"

    url = "https://nominatim.openstreetmap.org/search"
    params = {"format": "json", "q": query, "limit": 1, "addressdetails": 1}
    headers = {"User-Agent": "Datamundi-CityLens/1.0 (estudiante@sistemas.edu)"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            bbox = data[0].get("boundingbox")
            if bbox:
                bbox = [float(x) for x in bbox]  # [south, north, west, east]
            logger.info(
                f"✅ Coordenadas y bbox obtenidos para '{query}': {lat}, {lon}, bbox: {bbox}"
            )
            return lat, lon, bbox
        else:
            logger.warning(f"No se encontraron coordenadas para '{query}'")
            return None, None, None
    except requests.RequestException as e:
        logger.error(f"Error en geocoding para '{query}': {e}")
        return None, None, None


def sanitize_search_term(term):
    """
    Data Cleaning de Entrada: Estandariza la entrada del usuario.
    Convierte 'MéxIcO ' en 'mexico' para evitar duplicados en BD.
    """
    if not term:
        return ""
    term = (
        unicodedata.normalize("NFKD", term.strip())
        .encode("ASCII", "ignore")
        .decode("utf-8")
    )
    return term.lower()


def get_city_data(name):
    """
    Patrón Wrapper: Obtiene datos del país desde caché o REST Countries.
    """
    clean_name = sanitize_search_term(name)

    if not clean_name:
        logger.warning(f"Término de búsqueda inválido: '{name}'")
        return {"error": "Término de búsqueda inválido."}, 400

    try:
        # 1. Búsqueda en caché (PostgreSQL/SQLite)
        cached_city = City.query.filter(
            or_(City.search_name == clean_name, City.name.ilike(f"%{name}%"))
        ).first()

        if cached_city:
            logger.info(f"✅ Destino '{cached_city.name}' obtenido de caché")
            return {
                "name": cached_city.name,
                "country": cached_city.country,
                "population": cached_city.population,
                "timezone": cached_city.timezone,
                "iso_code": cached_city.iso_code,
                "lat": cached_city.lat,
                "lon": cached_city.lon,
                "bbox": [
                    cached_city.bbox_south,
                    cached_city.bbox_north,
                    cached_city.bbox_west,
                    cached_city.bbox_east,
                ]
                if cached_city.bbox_south
                else None,
            }

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error de base de datos al buscar ciudad: {str(e)}")
        return {"error": "Error de base de datos.", "detalle": str(e)}, 500

    # 🌐 Consulta a API externa usando variable de entorno
    url = f"{BASE_URL}/translation/{name}"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 404:
            url_capital = f"{BASE_URL}/capital/{name}"
            response = requests.get(url_capital, timeout=5)

        response.raise_for_status()
        payload = response.json()

        if not payload:
            return {"error": "No se encontraron datos."}, 404

        payload.sort(key=lambda x: x.get("population", 0), reverse=True)
        country_data = payload[0]

        capital_name = country_data.get("capital", [name])[0]
        country_name = country_data.get("name", {}).get("common", "Unknown")
        population = country_data.get("population", 0)
        timezone_str = country_data.get("timezones", ["UTC"])[0]
        iso_code = country_data.get("cca2", "")
        flag_url = country_data.get("flags", {}).get("svg", "")


        # 1. Prioridad: Geocodificar la CAPITAL del país (lugares populares cerca de la capital)
        # Esto evita el problema de bbox grandes que incluyen países vecinos
        lat, lon, bbox = get_city_coordinates(capital_name)

        # 2. Fallback: capitalInfo de REST Countries
        if lat is None or lon is None:
            capital_info = country_data.get("capitalInfo", {})
            capital_latlng = capital_info.get("latlng", [])

            if len(capital_latlng) >= 2:
                lat, lon = capital_latlng[0], capital_latlng[1]
                bbox = None
                logger.info(f"📍 Usando coordenadas de capital desde REST Countries: {capital_name}")

        # 3. Fallback final: Geocodificar el país (centroide)
        if lat is None or lon is None:
            lat, lon, bbox = get_city_coordinates(country_name)
            logger.info(f"📍 Usando coordenadas del país (centroide): {country_name}")
        # 2. Persistencia en la Base de Datos
        new_city = City(
            name=country_name,
            country=country_name,
            search_name=sanitize_search_term(country_name),
            population=population,
            timezone=timezone_str,
            iso_code=iso_code,
            flag_url=flag_url,
            capital=capital_name,
            lat=lat,
            lon=lon,
            bbox_south=bbox[0] if bbox else None,
            bbox_north=bbox[1] if bbox else None,
            bbox_west=bbox[2] if bbox else None,
            bbox_east=bbox[3] if bbox else None,
        )

        db.session.add(new_city)
        db.session.commit()

        return {
            "name": new_city.name,
            "country": new_city.country,
            "population": new_city.population,
            "timezone": new_city.timezone,
            "iso_code": new_city.iso_code,
            "lat": new_city.lat,
            "lon": new_city.lon,
            "bbox": bbox,
        }

    except requests.RequestException as e:
        db.session.rollback()
        return {"error": "API externa no disponible.", "detalle": str(e)}, 503

    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": "Error guardando en base de datos.", "detalle": str(e)}, 500


# --- LÓGICA DE FAVORITOS ---

def save_favorite(city_name, user_uuid):
    """Guarda un destino favorito vinculado a un UUID de sesión"""
    try:
        city = City.query.filter(City.name.ilike(f"%{city_name}%")).first()

        if not city:
            return {"error": "Busca la ciudad primero para poder guardarla."}, 404

        existing = Favorite.query.filter_by(user_uuid=user_uuid, city_id=city.id).first()
        if existing:
            return {"message": "Ya está en tus favoritos."}, 200

        new_fav = Favorite(user_uuid=user_uuid, city_id=city.id)
        db.session.add(new_fav)
        db.session.commit()

        return {"message": f"¡{city.name} guardado!"}, 201

    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Error de base de datos."}, 500


def get_favorites_by_user(user_uuid):
    """Recupera la lista de favoritos del usuario"""
    try:
        favorites = Favorite.query.filter_by(user_uuid=user_uuid).all()

        return [
            {
                "name": fav.city.name,
                "country": fav.city.country,
                "population": fav.city.population,
                "timezone": fav.city.timezone
            }
            for fav in favorites
        ], 200

    except SQLAlchemyError:
        return {"error": "Error al recuperar favoritos."}, 500