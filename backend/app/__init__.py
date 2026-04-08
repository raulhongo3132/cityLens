from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config

def create_app():
    """Crea y configura la aplicación Flask"""
    
    app = Flask(__name__)
    
    app.config.from_object(Config)

    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5500",
                "http://127.0.0.1:5500"
            ]
        }
    })

    @app.route("/api/ping", methods=["GET"])
    def ping():
        """Ruta de prueba para confirmar que el servidor corre."""
        return jsonify({"status": "ok"})
    
    return app