from app import create_app
from app.services.city_service import get_city_data

app = create_app()
with app.app_context():
    # Fetch Mexico (Should create it or hit API, or find existing)
    res = get_city_data("méxico")
    print(f"Result for 'méxico': {res.get('name')}")
    
    # Second fetch without accents (should hit cache using search_name)
    res2 = get_city_data("mexico")
    print(f"Result for 'mexico': {res2.get('name')}")
