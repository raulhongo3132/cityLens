import requests
import os
from app import db
from app.models import City, Place

CATEGORY_MAP = {
    'familiar': 'family friendly places',
    'gastronomico': 'restaurants',
    'nocturno': 'nightlife',
    'alternativo': 'alternative spots',
}


def _place_to_dict(place):
    return {
        "nombre": place.name,
        "rating": place.rating,
        "direccion": place.address,
        "horarios": place.hours,
    }


def _extract_hours(place_result):
    opening_hours = place_result.get("opening_hours", {})
    if isinstance(opening_hours, dict):
        if opening_hours.get("weekday_text"):
            return ", ".join(opening_hours.get("weekday_text", []))
        if opening_hours.get("open_now") is not None:
            return "Abierto ahora" if opening_hours.get("open_now") else "Cerrado ahora"
    return "Horario no disponible"

def get_places(city_name, category):
    """
    Obtiene lugares por ciudad y categoría con caché en base de datos.
    """
    try:
        city = City.query.filter_by(name=city_name).first()

        if city:
            cached_places = (
                Place.query.filter_by(city_id=city.id, category=category)
                .limit(10)
                .all()
            )
            if cached_places:
                return [_place_to_dict(place) for place in cached_places]

        api_key = os.getenv('GOOGLE_PLACES_KEY')
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        query = CATEGORY_MAP.get(category, category)
        params = {
            'query': f"{query} in {city_name}",
            'key': api_key
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if not city:
            city = City(name=city_name)
            db.session.add(city)
            db.session.flush()

        places_to_return = []
        for item in data.get("results", [])[:10]:
            place = Place(
                name=item.get("name"),
                rating=item.get("rating"),
                address=item.get("formatted_address"),
                hours=_extract_hours(item),
                category=category,
                city_id=city.id,
            )
            db.session.add(place)
            places_to_return.append(_place_to_dict(place))

        db.session.commit()
        return places_to_return

    except requests.RequestException as e:
        db.session.rollback()
        return {"error": "La API de Google Places no responde.", "detalle": str(e)}, 503
    except Exception:
        db.session.rollback()
        raise