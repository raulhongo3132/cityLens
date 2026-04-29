import requests
from sqlalchemy.exc import SQLAlchemyError
from app.models import db,City


def _serialize_city(city):
    data = {}
    for column in City.__table__.columns:
        data[column.name] = getattr(city, column.name)
    return data


def _set_if_exists(city, attr_name, value):
    if attr_name in City.__table__.columns.keys():
        setattr(city, attr_name, value)


def get_city_data(name):
    """
    Obtiene datos de ciudad con caché en base de datos y fallback a REST Countries.
    """
    try:
        cached_city = City.query.filter_by(name=name).first()
        if cached_city:
            print(f"✅ Ciudad {name} obtenida desde la caché (Base de datos)")
            return _serialize_city(cached_city)
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": "Error accediendo a la base de datos.", "detalle": str(e)}, 500

    print(f"🌐 Ciudad {name} no encontrada en caché. Consultando REST Countries API...")
    url = f"https://restcountries.com/v3.1/name/{name}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        payload = response.json()
        if not payload:
            return {"error": "No se encontraron datos para la ciudad solicitada."}, 404

        country_data = payload[0]
        city = City(name=name)

        _set_if_exists(city, "country", country_data.get("name", {}).get("common"))
        _set_if_exists(city, "region", country_data.get("region"))
        _set_if_exists(city, "subregion", country_data.get("subregion"))
        _set_if_exists(city, "population", country_data.get("population"))

        capitals = country_data.get("capital", [])
        if capitals:
            _set_if_exists(city, "capital", capitals[0])

        db.session.add(city)
        db.session.commit()
        return _serialize_city(city)
    except requests.RequestException as e:
        db.session.rollback()
        return {"error": "Servicio de ciudades no disponible temporalmente.", "detalle": str(e)}, 503
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": "Error guardando la ciudad en base de datos.", "detalle": str(e)}, 500