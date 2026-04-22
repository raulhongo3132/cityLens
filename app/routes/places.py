from flask import Blueprint, request, jsonify
from app.services.places_service import get_places

places = Blueprint('places', __name__)

@places.route('/api/places', methods=['GET'])
def places_endpoint():
    city = request.args.get('city')
    category = request.args.get('category')
    
    if not city or not category:
        return jsonify({"error": "Los parámetros 'city' y 'category' son requeridos"}), 400
        
    categorias_validas = ['familiar', 'gastronomico', 'nocturno', 'alternativo']
    if category not in categorias_validas:
        return jsonify({"error": f"Categoría inválida. Opciones: {', '.join(categorias_validas)}"}), 400

    result = get_places(city, category)

    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]

    return jsonify(result), 200