"""
app/security.py

Módulo de seguridad para proteger rutas sensibles con validación de API Key.
Implementa el patrón Decorator Pattern de GoF para interceptar y validar headers.

Responsabilidades:
- Validar presencia de header X-API-KEY
- Comparar el valor contra variable de entorno API_SECRET_KEY
- Retornar HTTP 401 Unauthorized si el header falta
- Retornar HTTP 403 Forbidden si el header no coincide
"""

import logging
import os
from functools import wraps

from flask import jsonify, request

logger = logging.getLogger(__name__)


def require_api_key(f):
    """
    Decorador que requiere un header X-API-KEY válido para acceder a la ruta.

    Uso:
        @app.route('/api/favorites', methods=['POST'])
        @require_api_key
        def crear_favorito():
            return jsonify({"message": "Favorito creado"})

    Validación:
        1. Extrae header X-API-KEY de request.headers
        2. Lee variable de entorno API_SECRET_KEY
        3. Compara valores con igualdad estricta (==)
        4. Si falta header: retorna 401 con mensaje descriptivo
        5. Si no coincide: retorna 403 con mensaje de acceso denegado

    Headers esperados:
        X-API-KEY: <valor_de_API_SECRET_KEY_en_.env>

    Respuestas:
        - 401 Unauthorized: header X-API-KEY ausente
        - 403 Forbidden: header X-API-KEY inválido o no coincide
        - Delegación a función original si validación pasa
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener el header X-API-KEY
        api_key_header = request.headers.get("X-API-KEY")

        # Leer la clave secreta del entorno
        api_secret_key = os.getenv("API_SECRET_KEY")

        # Validar presencia del header
        if not api_key_header:
            logger.warning(
                f"❌ Intento de acceso sin X-API-KEY desde {request.remote_addr}"
            )
            return (
                jsonify(
                    {
                        "error": "Unauthorized",
                        "message": "Header 'X-API-KEY' es requerido",
                    }
                ),
                401,
            )

        # Validar configuración del lado del servidor
        if not api_secret_key:
            logger.error("⚠️ API_SECRET_KEY no está configurada en .env")
            return (
                jsonify(
                    {
                        "error": "Internal Server Error",
                        "message": "API_SECRET_KEY no configurada en el servidor",
                    }
                ),
                500,
            )

        # Comparación estricta de la clave
        if api_key_header != api_secret_key:
            logger.warning(
                f"❌ Intento de acceso con X-API-KEY inválida desde {request.remote_addr}"
            )
            return (
                jsonify(
                    {
                        "error": "Forbidden",
                        "message": "X-API-KEY inválida o no autorizada",
                    }
                ),
                403,
            )

        # Si la validación pasa, loguear acceso exitoso
        logger.info(
            f"✅ Acceso autorizado a {request.path} desde {request.remote_addr}"
        )

        # Pasar el control a la función original
        return f(*args, **kwargs)

    return decorated_function
