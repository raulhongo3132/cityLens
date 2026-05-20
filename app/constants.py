# app/constants.py

PLACE_CATEGORIES = {
    "gastronomico": {
        "label": "Gastronómico",
        "osm_tags": [
            '["amenity"="restaurant"]',
            '["amenity"="cafe"]',
        ],
        "description": "Restaurantes y cafés destacados",
    },
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
            '["tourism"="information"]',
        ],
        "description": "Atracciones turísticas, parques temáticos y zoológicos",
    },
    "naturaleza": {
        "label": "Naturaleza",
        "osm_tags": [
            '["natural"="waterfall"]',
            '["natural"="peak"]',
            '["natural"="volcano"]',
            '["leisure"="nature_reserve"]',
            '["boundary"="national_park"]',
            '["tourism"="viewpoint"]',
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
            '["historic"="monument"]',
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
            '["historic"="archaeological_site"]',
            '["building"="cathedral"]',
        ],
        "description": "Monumentos, castillos, catedrales y sitios conmemorativos",
    },
}

BASE_CATEGORIES = list(PLACE_CATEGORIES.keys())
ALL_CATEGORIES = list(PLACE_CATEGORIES.keys())

# Nuevo diccionario para optimización de queries Overpass (Sección 18 IMPLEMENTATION_REPORT)
# Filtros con ["wikidata"] para priorizar lugares populares y bien documentados
OSM_CATEGORIES = {
    "gastronomico": [
        '["amenity"="restaurant"]["wikidata"]',
        '["amenity"="cafe"]["wikidata"]',
    ],
    "destacados": [
        '["tourism"="attraction"]["wikidata"]',
        '["historic"="monument"]["wikidata"]',
        '["historic"="building"]["wikidata"]',
    ],
    "turismo": [
        '["tourism"="attraction"]["wikidata"]',
        '["tourism"="viewpoint"]["wikidata"]',
        '["tourism"="theme_park"]["wikidata"]',
    ],
    "naturaleza": [
        '["leisure"="park"]["wikidata"]',
        '["natural"="water"]["wikidata"]',
    ],
    "cultura": [
        '["tourism"="museum"]["wikidata"]',
        '["tourism"="gallery"]["wikidata"]',
    ],
    "historico": [
        '["historic"="monument"]["wikidata"]',
        '["historic"="castle"]["wikidata"]',
        '["historic"="ruins"]["wikidata"]',
    ],
}