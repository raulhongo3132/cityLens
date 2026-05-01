from flask import Blueprint, jsonify, request

from app.constants import ALL_CATEGORIES
from app.services.places_service import get_places

places = Blueprint("places", __name__)


@places.route("/api/places", methods=["GET"])
def places_endpoint():
    city = request.args.get("city")
    category = request.args.get("category")

    if not city or not category:
        return jsonify(
            {"error": "Los parámetros 'city' y 'category' son requeridos"}
        ), 400

    if category not in ALL_CATEGORIES:
        return jsonify(
            {"error": f"Categoría inválida. Opciones: {', '.join(ALL_CATEGORIES)}"}
        ), 400

    result = get_places(city, category)

    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]

    return jsonify(result), 200
