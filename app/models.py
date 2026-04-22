#ARCHIVO TEMPORAL 
from flask_sqlalchemy import SQLAlchemy

# Inicializamos la instancia de la base de datos
db = SQLAlchemy()

class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    country = db.Column(db.String(100))
    region = db.Column(db.String(100))
    subregion = db.Column(db.String(100))
    population = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "region": self.region,
            "subregion": self.subregion,
            "population": self.population
        }

class Place(db.Model):
    __tablename__ = 'places'
    
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    rating = db.Column(db.Float)
    address = db.Column(db.String(250))
    # Para almacenar horarios u otra info estructurada, usamos JSON
    horarios = db.Column(db.JSON) 

    def to_dict(self):
        return {
            "id": self.id,
            "city_name": self.city_name,
            "category": self.category,
            "name": self.name,
            "rating": self.rating,
            "address": self.address,
            "horarios": self.horarios
        }