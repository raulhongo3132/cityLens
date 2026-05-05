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
    places = db.relationship("Place", backref="city", lazy=True)
    iso_code = db.Column(db.String(5), nullable=True)  # Código cca2 (ej. 'MX')
    flag_url = db.Column(db.String(255), nullable=True)  # URL de la bandera
    capital = db.Column(db.String(100), nullable=True)  # Nombre de la capital
    lat = db.Column(db.Float, nullable=True)  # Latitud central del país
    lon = db.Column(db.Float, nullable=True)  # Longitud central del país
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
        db.UniqueConstraint('city_id', 'osm_place_id', name='uq_city_osm_place'),
    )
