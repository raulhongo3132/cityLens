import sys
import logging
logging.basicConfig(level=logging.DEBUG)

from app import create_app
app = create_app()

with app.app_context():
    from app.services.osm_places import fetch_places_from_wrapper
    # Let's test with 'destacados' in Santiago de Chile
    # (lat=-33.45, lon=-70.67)
    res = fetch_places_from_wrapper("Santiago", -33.45, -70.67, "destacados", limit=3)
    if res and "elements" in res:
        for el in res["elements"]:
            tags = el.get("tags", {})
            name = tags.get("name", "Unnamed")
            lat = el.get("lat") or el.get("center", {}).get("lat")
            print(f"Found: {name} at {lat}")
    else:
        print("No elements or error.")
