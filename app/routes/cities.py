##############################################################################################################################
# ENDPOINTS:

##############################################################################################################################
from flask import Blueprint, jsonify, request

from app.services.city_service import get_city_data

# Se define el blueprint
cities = Blueprint("cities", __name__)


# 2. Ruta para la API (Devuelve el JSON y maneja la lógica)
@cities.route("/api/city", methods=["GET"])
def city_endpoint():
    name = request.args.get("name")

    if not name:
        return jsonify({"error": "El parámetro 'name' es requerido"}), 400

    # Delegamos la lógica al servicio importado correctamente
    result = get_city_data(name)

    # Si el servicio falla, devuelve una tupla con el error y el status (ej. 503)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]

    # Si es exitoso, devuelve los datos
    return jsonify(result), 200
