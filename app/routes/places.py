from flask import Blueprint, jsonify, request

places = Blueprint('places', __name__)

@places.route('/api/places')
def get_places():
    city = request.args.get('city', '')
    category = request.args.get('category', '')
    # Por ahora devuelve placeholder
    return jsonify({"city": city, "category": category, "places": []})