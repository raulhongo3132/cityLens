from flask import Blueprint, jsonify, request
# 1. Importamos las nuevas funciones del servicio
from app.services.city_service import get_city_data, save_favorite, get_favorites_by_user

# Se define el blueprint
cities = Blueprint("cities", __name__)

# --- RUTA EXISTENTE: Búsqueda de ciudad ---
@cities.route("/api/city", methods=["GET"])
def city_endpoint():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "El parámetro 'name' es requerido"}), 400

    result = get_city_data(name)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result), 200


# 👇 2. NUEVA RUTA: Guardar Favorito (POST)
# Arquitectura: Usamos POST porque estamos creando un recurso en la DB.
@cities.route("/api/favorites", methods=["POST"])
def add_favorite():
    data = request.get_json() # Esperamos un JSON del frontend
    
    if not data or 'city_name' not in data or 'user_uuid' not in data:
        return jsonify({"error": "Faltan datos (city_name y user_uuid son requeridos)"}), 400

    # Llamamos al cocinero (servicio)
    result = save_favorite(data['city_name'], data['user_uuid'])
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result), 201


# 👇 3. NUEVA RUTA: Listar Favoritos (GET)
# Arquitectura: Usamos GET para recuperar la lista del Momento B.
@cities.route("/api/favorites", methods=["GET"])
def list_favorites():
    user_uuid = request.args.get("uuid")
    
    if not user_uuid:
        return jsonify({"error": "El parámetro 'uuid' es requerido"}), 400

    result = get_favorites_by_user(user_uuid)
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    return jsonify(result), 200