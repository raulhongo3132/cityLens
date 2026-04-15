from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from flask_sqlalchemy import SQLAlchemy
import os

# 1. Inicializar la instancia (sin la app aún)
db = SQLAlchemy()

def create_app():
    """Crea y configura la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Carga la configuración (asegúrate que Config.SQLALCHEMY_DATABASE_URI 
    # use el host 127.0.0.1 para evitar el error de 'Peer authentication')
    app.config.from_object(Config)

    # 2. Vincular db con la app
    db.init_app(app)

    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5500",
                "http://127.0.0.1:5500"
            ]
        }
    })

    # 3. Registrar modelos y crear tablas
    with app.app_context():
        # Importante: Importar los modelos aquí para que SQLAlquemy los "vea"
        from . import models 
        
        # Crear tablas si no existen
        db.create_all()
        print("¡Base de datos sincronizada!")

    @app.route("/api/ping", methods=["GET"])
    def ping():
        """Ruta de prueba para confirmar que el servidor corre."""
        return jsonify({"status": "ok"})
    
    return app