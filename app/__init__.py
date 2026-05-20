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
    from app.routes.places import places
    from app.routes.main import main
    from app.routes.favorites import favorites
    from app.routes.docs import docs

    app.register_blueprint(cities)
    app.register_blueprint(places)
    app.register_blueprint(favorites)
    app.register_blueprint(docs)
    app.register_blueprint(main)

    logger.info("✅ Blueprints registrados exitosamente")

    # 🗑️ RESET_ON_STARTUP: Limpia la base de datos al iniciar (útil para Render)
    # Para activar: agregar variable de entorno RESET_ON_STARTUP=true en Render
    if os.getenv("RESET_ON_STARTUP", "false").lower() == "true":
        with app.app_context():
            from app.models import City, Place

            try:
                # Eliminar en orden inverso a las foreign keys
                Place.query.delete()
                City.query.delete()
                db.session.commit()
                logger.info("🗑️ RESET_ON_STARTUP: Base de datos limpiada exitosamente")
            except Exception as e:
                db.session.rollback()
                logger.error(f"🗑️ RESET_ON_STARTUP: Error al limpiar BD: {e}")

    return app