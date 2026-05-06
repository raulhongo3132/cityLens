import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

# 1. AQUÍ NACE LA ÚNICA INSTANCIA (El candado único)
db = SQLAlchemy()
migrate = Migrate()


# 2. Configurar logging estructurado
def setup_logging():
    """Configura logging con formato estructurado"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console output
        ],
    )
    return logging.getLogger(__name__)


def create_app():
    # Eliminamos las rutas relativas. Flask buscará 'templates' y 'static' dentro de 'app' por defecto.
    app = Flask(__name__)

    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("🚀 Iniciando CityLens App Factory")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    origen_permitido = os.getenv("ORIGEN_PERMITIDO", "http://127.0.0.1:5500")
    CORS(app, resources={r"/api/*": {"origins": origen_permitido}})

    # 2. VINCULAMOS LA INSTANCIA A LA APP
    db.init_app(app)
    migrate.init_app(app, db)

    # 3. IMPORTACIONES DIFERIDAS
    with app.app_context():
        from app import models

    # 4. Registramos los Blueprints (Tus Meseros y tu Recepcionista)
    from app.routes.cities import cities
    from app.routes.favorites import (
        favorites,  # Importamos rutas de favoritos con seguridad
    )
    from app.routes.docs import docs  # Importamos documentación Swagger
    from app.routes.main import main  # Importamos al Recepcionista oficial
    from app.routes.places import places

    app.register_blueprint(cities)
    app.register_blueprint(places)
    app.register_blueprint(favorites)  # Rutas protegidas con @require_api_key
    app.register_blueprint(docs)  # Documentación Swagger UI
    app.register_blueprint(main)  # Le damos el control de la ruta "/" y "/city"

    logger.info("✅ Blueprints registrados exitosamente")

    return app
