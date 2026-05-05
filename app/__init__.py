import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

# 1. Instancia única
db = SQLAlchemy()
migrate = Migrate()


# 2. Logging estructurado
def setup_logging():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("🚀 Iniciando CityLens App Factory")

    # 🔐 Variables de entorno (SIN hardcode)
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("❌ DATABASE_URL no está definida en variables de entorno")

    origen_permitido = os.getenv("ORIGEN_PERMITIDO")
    if not origen_permitido:
        raise RuntimeError("❌ ORIGEN_PERMITIDO no está definida en variables de entorno")

    # Configuración Flask
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # CORS dinámico desde env
    CORS(app, resources={r"/api/*": {"origins": origen_permitido}})

    # 3. Inicialización
    db.init_app(app)
    migrate.init_app(app, db)

    # 4. Importaciones diferidas
    with app.app_context():
        from app import models

    # 5. Blueprints
    from app.routes.cities import cities
    from app.routes.main import main
    from app.routes.places import places

    app.register_blueprint(cities)
    app.register_blueprint(places)
    app.register_blueprint(main)

    logger.info("✅ Blueprints registrados exitosamente")

    return app