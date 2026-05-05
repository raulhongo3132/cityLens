##############################################################################################################################
# LOGICA DEL NEGOCIO: services/places_service.py
##############################################################################################################################
import logging

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import City, Place
from app.services.osm_places import fetch_places_from_wrapper

logger = logging.getLogger(__name__)


def get_places(city_name, category):
    try:
        # 1. Verificar en "La Despensa" (buscar por nombre o capital)
        city = City.query.filter(
            or_(
                City.name.ilike(f"%{city_name}%"),
                City.capital.ilike(f"%{city_name}%"),
            )
        ).first()
        if not city:
            from app.services.city_service import get_city_data

            city_result = get_city_data(city_name)
            if isinstance(city_result, tuple):
                return city_result

            city = City.query.filter_by(name=city_result["name"]).first()
            if not city:
                logger.error(f"No se pudo crear la ciudad '{city_name}'.")
                return {"error": f"No se pudo crear la ciudad '{city_name}'."}, 500

        # 2. Verificar caché de lugares
        cached_places = (
            Place.query.filter_by(city_id=city.id, category=category).limit(10).all()
        )
        if cached_places:
            logger.info(f"✅ Lugares de {city_name} obtenidos de caché (PostgreSQL)")
            return [
                {
                    "name": p.name,
                    "address": p.address,
                    "category": p.category,
                    "lat": p.latitude,
                    "lon": p.longitude,
                    "website": p.website,
                    "phone": p.phone,
                    "opening_hours": p.opening_hours,
                }
                for p in cached_places
            ]

        logger.info("🌐 Consultando OpenStreetMap a través del wrapper...")

        # Verificar que tengamos coordenadas válidas
        if not city.lat or not city.lon:
            logger.error(
                f"Coordenadas faltantes para '{city.name}' (lat={city.lat}, lon={city.lon})"
            )
            return {
                "error": "No se encontraron coordenadas para la ciudad. Intenta de nuevo."
            }, 400

        # Pasamos coordenadas exactas (requiere GET y no POST para Overpass)
        osm_data = fetch_places_from_wrapper(
            city_name=city.name,
            latitude=city.lat,
            longitude=city.lon,
            category=category,
            limit=10,
        )

        if not osm_data or "elements" not in osm_data:
            logger.warning(
                f"No se encontraron lugares para '{category}' en {city_name}"
            )
            return {
                "error": "No se encontraron lugares o falló la conexión con OpenStreetMap."
            }, 404

        # 4. Fase de Data Cleaning
        places_to_return = []

        for idx, element in enumerate(osm_data["elements"], 1):
            tags = element.get("tags", {})

            name = tags.get("name:es") or tags.get("name:en") or tags.get("int_name") or tags.get("name")
            if not name:
                continue

            street = tags.get("addr:street", "")
            housenumber = tags.get("addr:housenumber", "")
            address = f"{street} {housenumber}".strip()

            if not address:
                address = "Dirección no especificada en el mapa"

            lat = element.get("lat")
            lon = element.get("lon")

            if not lat or not lon:
                center = element.get("center", {})
                lat = center.get("lat")
                lon = center.get("lon")

            # 👇 NUEVA EXTRACCIÓN: Sacamos la info extra del "Mercado Libre"
            website = tags.get("website", tags.get("contact:website", ""))
            phone = tags.get("phone", tags.get("contact:phone", ""))
            opening_hours = tags.get("opening_hours", "")

            # Persistencia de datos enriquecidos
            place = Place(
                city_id=city.id,
                name=name,
                category=category,
                rating=0.0,
                address=address,
                osm_place_id=str(element.get("id", "")),
                latitude=lat,
                longitude=lon,
                website=website[:255] if website else None,
                phone=phone[:50] if phone else None,
                opening_hours=opening_hours[:255] if opening_hours else None,
            )

            db.session.add(place)
            places_to_return.append(
                {
                    "name": place.name,
                    "address": place.address,
                    "category": place.category,
                    "lat": lat,
                    "lon": lon,
                    "website": place.website,
                    "phone": place.phone,
                    "opening_hours": place.opening_hours,
                }
            )

        if not places_to_return:
            logger.warning(
                f"No hay lugares comerciales registrados como '{category}' en {city_name}"
            )
            return {
                "error": f"Se encontraron datos, pero no hay negocios registrados como '{category}' aquí."
            }, 404

        # 🛡️ PROTECCIÓN: Commit con validación de duplicados
        try:
            db.session.commit()
            logger.info(
                f"✅ {len(places_to_return)} lugares guardados en caché para {city_name}/{category}"
            )
        except Exception as e:
            db.session.rollback()

            # Si el error es por restricción única, intenta insertar uno por uno
            if (
                "IntegrityError" in str(type(e).__name__)
                or "duplicate" in str(e).lower()
                or "unique" in str(e).lower()
            ):
                logger.warning(
                    f"⚠️ Algunos lugares podrían estar duplicados. "
                    f"Insertando selectivamente para {city_name}..."
                )
                places_to_return = []
                for idx, element in enumerate(osm_data["elements"], 1):
                    tags = element.get("tags", {})
                    name = tags.get("name:es") or tags.get("name:en") or tags.get("int_name") or tags.get("name")
                    if not name:
                        continue

                    osm_place_id = str(element.get("id", ""))

                    # Verificar si ya existe el lugar para esta ciudad
                    existing = Place.query.filter_by(
                        city_id=city.id, osm_place_id=osm_place_id
                    ).first()

                    if existing:
                        logger.debug(
                            f"Lugar {osm_place_id} ({name}) ya existe, omitiendo..."
                        )
                        # Agregarlo al resultado de todas formas (ya está en la BD)
                        places_to_return.append(
                            {
                                "name": existing.name,
                                "address": existing.address,
                                "category": existing.category,
                                "lat": existing.latitude,
                                "lon": existing.longitude,
                                "website": existing.website,
                                "phone": existing.phone,
                                "opening_hours": existing.opening_hours,
                            }
                        )
                        continue

                    street = tags.get("addr:street", "")
                    housenumber = tags.get("addr:housenumber", "")
                    address = f"{street} {housenumber}".strip()
                    if not address:
                        address = "Dirección no especificada en el mapa"

                    lat = element.get("lat")
                    lon = element.get("lon")
                    if not lat or not lon:
                        center = element.get("center", {})
                        lat = center.get("lat")
                        lon = center.get("lon")

                    website = tags.get("website", tags.get("contact:website", ""))
                    phone = tags.get("phone", tags.get("contact:phone", ""))
                    opening_hours = tags.get("opening_hours", "")

                    try:
                        place = Place(
                            city_id=city.id,
                            name=name,
                            category=category,
                            rating=0.0,
                            address=address,
                            osm_place_id=osm_place_id,
                            latitude=lat,
                            longitude=lon,
                            website=website[:255] if website else None,
                            phone=phone[:50] if phone else None,
                            opening_hours=opening_hours[:255]
                            if opening_hours
                            else None,
                        )
                        db.session.add(place)
                        db.session.commit()

                        places_to_return.append(
                            {
                                "name": place.name,
                                "address": place.address,
                                "category": place.category,
                                "lat": lat,
                                "lon": lon,
                                "website": place.website,
                                "phone": place.phone,
                                "opening_hours": place.opening_hours,
                            }
                        )
                    except Exception as inner_e:
                        db.session.rollback()
                        logger.debug(
                            f"No se pudo insertar lugar {osm_place_id}: {inner_e}"
                        )
                        continue

                logger.info(
                    f"✅ {len(places_to_return)} lugares recuperados/insertados para {city_name}/{category}"
                )
            else:
                logger.error(f"❌ Error inesperado al insertar lugares: {e}")
                raise
        logger.info(
            f"✅ {len(places_to_return)} lugares guardados en caché para {city_name}/{category}"
        )
        return places_to_return

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error de base de datos: {str(e)}")
        return {"error": "Error de base de datos.", "detalle": str(e)}, 500
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return {"error": "Error inesperado en el servicio.", "detalle": str(e)}, 500
