from flask import Blueprint, render_template, request

cities = Blueprint('cities', __name__)

@cities.route('/city')
def city():
    name = request.args.get('name', '')
    return render_template('city.html', city_name=name)