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
        "horarios": place.opening_hours,
    }

def _extract_country(formatted_address):
    """
    Extrae el país de la dirección formateada de Google.
    Google suele poner el país al final: 'Calle Falsa 123, CABA, Argentina'
    """
    if not formatted_address:
        return "Unknown"
    parts = formatted_address.split(',')
    return parts[-1].strip()

def _extract_hours(place_result):
    opening_hours = place_result.get("opening_hours", {})
    if isinstance(opening_hours, dict):
        weekday_text = opening_hours.get("weekday_text")
        if weekday_text:
            return ", ".join(weekday_text)
        
        open_now = opening_hours.get("open_now")
        if open_now is not None:
            return "Abierto ahora" if open_now else "Cerrado ahora"
    return "Horario no disponible"

def get_places(city_name, category):
    
    city_name = city_name.strip().title()
    
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
        query_term = CATEGORY_MAP.get(category, category)

        params = {
            'query': f"{query_term} in {city_name}",
            'key': api_key,
            'language': 'es'
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if not results:
            return []

        
        detected_country = _extract_country(results.get("formatted_address"))

        
        if not city:
            city = City(
                name=city_name,
                country=detected_country
            )
            db.session.add(city)
            db.session.flush()

        places_to_return = []
        for item in results[:10]:
            
            name = item.get("name")
            existing_p = Place.query.filter_by(name=name, city_id=city.id).first()
            
            if not existing_p:
                place = Place(
                    name=name,
                    rating=item.get("rating"),
                    address=item.get("formatted_address"),
                    opening_hours=_extract_hours(item),
                    category=category,
                    city_id=city.id,
                )
                db.session.add(place)
                places_to_return.append(_place_to_dict(place))
            else:
                places_to_return.append(_place_to_dict(existing_p))

        db.session.commit()
        return places_to_return

    except Exception as e:
        db.session.rollback()
        print(f"Error en get_places: {e}")
        return {"error": "No se pudieron obtener los lugares", "detalle": str(e)}