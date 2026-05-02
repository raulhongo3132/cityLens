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

    # 1. Data Cleaning de Entrada
    clean_category = category.lower().strip()

    # 2. Validación de Seguridad Estricta
    if clean_category not in ALL_CATEGORIES:
        return jsonify(
            {
                "error": f"Categoría inválida '{category}'. Opciones: {', '.join(ALL_CATEGORIES)}"
            }
        ), 400

    # 3. 👇 CORRECCIÓN CRÍTICA: Le entregamos a "El Cocinero" el ingrediente YA LIMPIO (clean_category)
    result = get_places(city, clean_category)

    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]

    return jsonify(result), 200
