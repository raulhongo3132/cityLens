from . import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON


class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)

    # Nombre de la ciudad (usado en búsquedas)
    name = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    country = db.Column(
        db.String(100),
        nullable=False
    )

    population = db.Column(db.Integer)

    timezone = db.Column(db.String(50))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relación: una ciudad tiene muchos lugares
    places = db.relationship(
        "Place",
        backref="city",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<City {self.name}, {self.country}>"


class Place(db.Model):
    __tablename__ = "places"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Foreign Key hacia City
    city_id = db.Column(
        db.Integer,
        db.ForeignKey("cities.id"),
        nullable=False,
        index=True
    )

    name = db.Column(
        db.String(200),
        nullable=False,
        index=True
    )

    # Categoría usada por los endpoints
    category = db.Column(
        db.String(100),
        index=True
    )

    rating = db.Column(db.Float)

    address = db.Column(db.String(500))

    # ID único de Google Places
    google_place_id = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    price_level = db.Column(db.Integer)

    # Horarios almacenados en formato JSON (PostgreSQL)
    opening_hours = db.Column(JSON)

    cached_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<Place {self.name} ({self.category})>"
