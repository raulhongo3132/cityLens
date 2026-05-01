# app/constants.py
# Constantes globales de la aplicación
# Centraliza configuraciones para sincronización entre frontend y backend

# Categorías de lugares disponibles (Calibrado con métricas de OSM TagInfo)
PLACE_CATEGORIES = {
    "turismo": {
        "label": "Turismo",
        "osm_tags": [
            '["tourism"="attraction"]',  # Atracciones generales (1.5M+ registros)
            '["tourism"="theme_park"]',  # Parques de diversiones
            '["tourism"="zoo"]',  # Zoológicos
            '["tourism"="aquarium"]',  # Acuarios
            '["tourism"="viewpoint"]',  # Miradores turísticos reconocidos
        ],
        "description": "Atracciones turísticas, parques temáticos y zoológicos",
    },
    "naturaleza": {
        "label": "Naturaleza",
        "osm_tags": [
            '["boundary"="national_park"]',  # Parques nacionales oficiales
            '["leisure"="nature_reserve"]',  # Reservas ecológicas
            '["natural"="waterfall"]',  # Cascadas con nombre propio
            '["natural"="peak"]',  # Montañas y picos importantes
            '["natural"="volcano"]',  # Volcanes
        ],
        "description": "Parques nacionales, reservas ecológicas y maravillas naturales",
    },
    "cultura": {
        "label": "Cultura",
        "osm_tags": [
            '["tourism"="museum"]',  # Museos (Alta probabilidad de tener web y horarios)
            '["tourism"="gallery"]',  # Galerías de arte
            '["amenity"="theatre"]',  # Teatros
            '["amenity"="arts_centre"]',  # Centros culturales
            '["historic"="archaeological_site"]',  # Zonas arqueológicas (Pirámides, ruinas)
        ],
        "description": "Museos, teatros, galerías y zonas arqueológicas",
    },
    "historico": {
        "label": "Histórico",
        "osm_tags": [
            '["historic"="monument"]',  # Monumentos conmemorativos
            '["historic"="memorial"]',  # Memoriales
            '["historic"="castle"]',  # Castillos y fortalezas
            '["historic"="ruins"]',  # Ruinas históricas
            '["building"="cathedral"]',  # Catedrales de valor histórico
        ],
        "description": "Monumentos, castillos, catedrales y sitios conmemorativos",
    },
}

# Generamos la lista de categorías dinámicamente desde las llaves del diccionario principal
BASE_CATEGORIES = list(PLACE_CATEGORIES.keys())

# Lista de todas las categorías disponibles para inyectar en Jinja2
ALL_CATEGORIES = list(PLACE_CATEGORIES.keys())
