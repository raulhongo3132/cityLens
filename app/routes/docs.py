from flask import Blueprint, render_template

docs = Blueprint("docs", __name__)


@docs.route("/docs")
def swagger_ui():
    """Renderiza la interfaz Swagger UI para la documentación de la API."""
    return render_template("swagger.html")
