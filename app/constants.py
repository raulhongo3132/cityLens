# app/constants.py

PLACE_CATEGORIES = {
    # 👇 NUEVA CATEGORÍA POR DEFECTO
    "destacados": {
        "label": "Destacados",
        "osm_tags": [
            '["tourism"="attraction"]',
            '["historic"="monument"]',
            '["tourism"="museum"]',
            '["boundary"="national_park"]',
        ],
        "description": "Los lugares más populares y representativos del país",
    },
    "turismo": {
        "label": "Turismo",
        "osm_tags": [
            '["tourism"="attraction"]',
            '["tourism"="theme_park"]',
            '["tourism"="zoo"]',
            '["tourism"="aquarium"]',
            '["tourism"="viewpoint"]',
        ],
        "description": "Atracciones turísticas, parques temáticos y zoológicos",
    },
    "naturaleza": {
        "label": "Naturaleza",
        "osm_tags": [
            '["boundary"="national_park"]',
            '["leisure"="nature_reserve"]',
            '["natural"="waterfall"]',
            '["natural"="peak"]',
            '["natural"="volcano"]',
        ],
        "description": "Parques nacionales, reservas ecológicas y maravillas naturales",
    },
    "cultura": {
        "label": "Cultura",
        "osm_tags": [
            '["tourism"="museum"]',
            '["tourism"="gallery"]',
            '["amenity"="theatre"]',
            '["amenity"="arts_centre"]',
            '["historic"="archaeological_site"]',
        ],
        "description": "Museos, teatros, galerías y zonas arqueológicas",
    },
    "historico": {
        "label": "Histórico",
        "osm_tags": [
            '["historic"="monument"]',
            '["historic"="memorial"]',
            '["historic"="castle"]',
            '["historic"="ruins"]',
            '["building"="cathedral"]',
        ],
        "description": "Monumentos, castillos, catedrales y sitios conmemorativos",
    },
}

BASE_CATEGORIES = list(PLACE_CATEGORIES.keys())
ALL_CATEGORIES = list(PLACE_CATEGORIES.keys())
