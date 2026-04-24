from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Crear la instancia de la base de datos
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Cargar configuración (base de datos, etc.)
    app.config.from_object(Config)

    # Inicializar la base de datos con la app
    db.init_app(app)

    # Registrar blueprints
    from app.routes.main import main
    from app.routes.cities import cities
    from app.routes.places import places

    app.register_blueprint(main)
    app.register_blueprint(cities)
    app.register_blueprint(places)

    # 🔴 IMPORTANTE: Registrar modelos y crear tablas
    with app.app_context():
        from app import models
        db.create_all()
        print("Base de datos sincronizada")

    return app