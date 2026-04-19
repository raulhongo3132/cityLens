from flask import Blueprint, render_template, request, redirect, url_for

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/city')
def city():
    name = request.args.get('name', '').strip()
    if not name:
        return redirect(url_for('main.index'))
    return render_template('city.html', city_name=name)
