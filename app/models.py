from datetime import datetime
from . import db

class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    population = db.Column(db.Integer)
    timezone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    places = db.relationship("Place", backref="city", lazy=True)

    # Relación con favoritos (de karla)
    favorites = db.relationship(
        "Favorite",
        backref="city",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # Datos de país
    iso_code = db.Column(db.String(5), nullable=True)
    flag_url = db.Column(db.String(255), nullable=True)
    capital = db.Column(db.String(100), nullable=True)

    # Coordenadas
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)

    # Bounding box (de upgrade)
    bbox_south = db.Column(db.Float, nullable=True)
    bbox_north = db.Column(db.Float, nullable=True)
    bbox_west = db.Column(db.Float, nullable=True)
    bbox_east = db.Column(db.Float, nullable=True)

    search_name = db.Column(db.String(100), nullable=True)

class Place(db.Model):
    __tablename__ = "places"
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    rating = db.Column(db.Float)
    address = db.Column(db.String(500))
    osm_place_id = db.Column(db.String(255))
    price_level = db.Column(db.Integer)
    opening_hours = db.Column(db.String(255))
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("city_id", "osm_place_id", name="uq_city_osm_place"),
    )

# 👇 NUEVA TABLA: El corazón de tu Propuesta de Valor Única (PVU)
class Favorite(db.Model):
    __tablename__ = "favorites"
    id = db.Column(db.Integer, primary_key=True)
    # Este UUID se generará en el frontend y se guardará en LocalStorage
    user_uuid = db.Column(db.String(100), nullable=False, index=True)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Restricción: Un usuario no puede agregar la misma ciudad dos veces a favoritos
    __table_args__ = (
        db.UniqueConstraint('user_uuid', 'city_id', name='uq_user_favorite_city'),
    )