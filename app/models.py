from . import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    country = db.Column(
        db.String(100),
        nullable=False
    )

    population = db.Column(db.Integer)

    timezone = db.Column(db.String(50))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    places = db.relationship(
        "Place",
        backref="city",
        lazy=True
    )


class Place(db.Model):
    __tablename__ = "places"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    city_id = db.Column(
        db.Integer,
        db.ForeignKey("cities.id"),
        nullable=False
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    category = db.Column(db.String(100))

    rating = db.Column(db.Float)

    address = db.Column(db.String(500))

    google_place_id = db.Column(
        db.String(255),
        unique=True
    )

    price_level = db.Column(db.Integer)

    opening_hours = db.Column(JSON)

    cached_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )