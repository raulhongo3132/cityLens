from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Registrar blueprints
    from app.routes.main import main
    from app.routes.cities import cities
    from app.routes.places import places

    app.register_blueprint(main)
    app.register_blueprint(cities)
    app.register_blueprint(places)

    return app