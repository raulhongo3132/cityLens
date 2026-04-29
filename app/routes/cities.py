from flask import Blueprint, request, jsonify, render_template
from app.services.city_service import get_city_data

# Se define el blueprint
cities = Blueprint('cities', __name__)

# 1. Ruta para la interfaz web (Renderiza el HTML)
@cities.route('/city', methods=['GET'])
def city_page():
    name = request.args.get('name', '')
    return render_template('city.html', city_name=name)

# 2. Ruta para la API (Devuelve el JSON y maneja la lógica)
@cities.route('/api/city', methods=['GET'])
def city_endpoint():
    name = request.args.get('name')

    if not name:
        return jsonify({"error": "El parámetro 'name' es requerido"}), 400

    # Delegamos la lógica al servicio importado correctamente
    result = get_city_data(name)

    # Si el servicio falla, devuelve una tupla con el error y el status (ej. 503)
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]

    # Si es exitoso, devuelve los datos
    return jsonify(result), 200