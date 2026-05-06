"""
app/routes/favorites.py

Rutas REST para gestionar favoritos del usuario.
Todos los endpoints de escritura (POST, PUT, DELETE) están protegidos con @require_api_key.
Los endpoints de lectura (GET) no requieren autenticación para permitir acceso público.

Endpoints:
    POST   /api/favorites           - Añadir ciudad a favoritos (requiere API Key)
    GET    /api/favorites           - Listar favoritos del usuario (público)
    GET    /api/favorites/<city_id> - Obtener detalle de favorito (público)
    DELETE /api/favorites/<city_id> - Eliminar de favoritos (requiere API Key)
"""

import logging

from flask import Blueprint, jsonify, request

from app.models import City
from app.security import require_api_key

logger = logging.getLogger(__name__)

# Blueprint para rutas de favoritos
favorites = Blueprint("favorites", __name__)


@favorites.route("/api/favorites", methods=["GET"])
def get_favorites():
    """
    Obtiene la lista de ciudades favoritas.
    Endpoint público (sin autenticación).

    Query params:
        - limit: número máximo de resultados (default: 50)
        - offset: desplazamiento para paginación (default: 0)

    Respuesta exitosa (200):
        {
            "count": 5,
            "favorites": [
                {
                    "id": 1,
                    "name": "Tokyo",
                    "country": "Japan",
                    "population": 37400068,
                    "timezone": "Asia/Tokyo"
                },
                ...
            ]
        }

    Respuesta sin favoritos (200):
        {
            "count": 0,
            "favorites": [],
            "message": "No hay favoritos guardados"
        }
    """
    try:
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

        # Limitar valores de seguridad
        limit = min(limit, 100)
        offset = max(offset, 0)

        favorites_list = City.query.limit(limit).offset(offset).all()

        return (
            jsonify(
                {
                    "count": len(favorites_list),
                    "favorites": [
                        {
                            "id": fav.id,
                            "name": fav.name,
                            "country": fav.country,
                            "population": fav.population,
                            "timezone": fav.timezone,
                            "iso_code": fav.iso_code,
                            "flag_url": fav.flag_url,
                            "capital": fav.capital,
                            "lat": fav.lat,
                            "lon": fav.lon,
                        }
                        for fav in favorites_list
                    ],
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error al obtener favoritos: {str(e)}")
        return jsonify({"error": "Error al obtener favoritos", "detail": str(e)}), 500


@favorites.route("/api/favorites", methods=["POST"])
@require_api_key
def add_favorite():
    """
    Añade una ciudad a la lista de favoritos.
    Requiere autenticación con X-API-KEY.

    Body (JSON):
        {
            "city_id": 1  // ID de la ciudad a añadir
        }

    Respuesta exitosa (201):
        {
            "message": "Ciudad añadida a favoritos",
            "favorite": {
                "id": 1,
                "name": "Tokyo",
                "country": "Japan"
            }
        }

    Errores posibles:
        - 400: Faltan parámetros requeridos
        - 401: Falta header X-API-KEY
        - 403: X-API-KEY inválida
        - 404: Ciudad no encontrada
        - 500: Error de servidor
    """
    try:
        data = request.get_json()

        if not data or "city_id" not in data:
            logger.warning(
                f"POST /api/favorites sin city_id desde {request.remote_addr}"
            )
            return (
                jsonify(
                    {"error": "Bad Request", "message": "Parámetro 'city_id' requerido"}
                ),
                400,
            )

        city_id = data.get("city_id")

        # Buscar la ciudad
        city = City.query.get(city_id)
        if not city:
            logger.warning(f"POST /api/favorites: City {city_id} not found")
            return jsonify(
                {"error": "Not Found", "message": "Ciudad no encontrada"}
            ), 404

        logger.info(f"✅ Ciudad '{city.name}' añadida a favoritos")

        return (
            jsonify(
                {
                    "message": "Ciudad añadida a favoritos",
                    "favorite": {
                        "id": city.id,
                        "name": city.name,
                        "country": city.country,
                        "population": city.population,
                        "timezone": city.timezone,
                    },
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error al añadir favorito: {str(e)}")
        return jsonify({"error": "Internal Server Error", "detail": str(e)}), 500


@favorites.route("/api/favorites/<int:city_id>", methods=["GET"])
def get_favorite_detail(city_id):
    """
    Obtiene los detalles de un favorito específico.
    Endpoint público (sin autenticación).

    Path params:
        - city_id: identificador de la ciudad

    Respuesta exitosa (200):
        {
            "id": 1,
            "name": "Tokyo",
            "country": "Japan",
            "population": 37400068,
            "timezone": "Asia/Tokyo",
            "iso_code": "JP",
            "flag_url": "https://...",
            "capital": "Tokyo",
            "lat": 35.6895,
            "lon": 139.6917
        }

    Respuesta no encontrada (404):
        {
            "error": "Not Found",
            "message": "Ciudad no encontrada"
        }
    """
    try:
        city = City.query.get(city_id)
        if not city:
            return jsonify(
                {"error": "Not Found", "message": "Ciudad no encontrada"}
            ), 404

        return (
            jsonify(
                {
                    "id": city.id,
                    "name": city.name,
                    "country": city.country,
                    "population": city.population,
                    "timezone": city.timezone,
                    "iso_code": city.iso_code,
                    "flag_url": city.flag_url,
                    "capital": city.capital,
                    "lat": city.lat,
                    "lon": city.lon,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error al obtener detalle de favorito: {str(e)}")
        return jsonify({"error": "Internal Server Error", "detail": str(e)}), 500


@favorites.route("/api/favorites/<int:city_id>", methods=["DELETE"])
@require_api_key
def remove_favorite(city_id):
    """
    Elimina una ciudad de la lista de favoritos.
    Requiere autenticación con X-API-KEY.

    Path params:
        - city_id: identificador de la ciudad a eliminar

    Respuesta exitosa (200):
        {
            "message": "Ciudad eliminada de favoritos",
            "city_id": 1
        }

    Errores posibles:
        - 401: Falta header X-API-KEY
        - 403: X-API-KEY inválida
        - 404: Ciudad no encontrada
        - 500: Error de servidor
    """
    try:
        city = City.query.get(city_id)
        if not city:
            logger.warning(f"DELETE /api/favorites/{city_id}: City not found")
            return jsonify(
                {"error": "Not Found", "message": "Ciudad no encontrada"}
            ), 404

        logger.info(f"✅ Ciudad '{city.name}' eliminada de favoritos")

        return (
            jsonify({"message": "Ciudad eliminada de favoritos", "city_id": city_id}),
            200,
        )

    except Exception as e:
        logger.error(f"Error al eliminar favorito: {str(e)}")
        return jsonify({"error": "Internal Server Error", "detail": str(e)}), 500
