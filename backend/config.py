import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),".env")
load_dotenv(dotenv_path)

class Config:
    """Configuración principal de la app Flask."""
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    SECRET_KEY = os.getenv("SECRET_KEY","supersecretkey")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
