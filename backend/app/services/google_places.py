import requests
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")

def search_places(city_name: str, category: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Busca lugares usando Foursquare API con lógica de reintentos para conexiones inestables.
    """
    url = "https://api.foursquare.com/v3/places/search"
    
    if not FOURSQUARE_API_KEY:
        print("⚠️ Error: No se encontró FOURSQUARE_API_KEY en el entorno.")
        return []

    params = {
        "near": city_name,
        "query": category,
        "limit": limit
    }
    
    headers = {
        "accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY,
        "Connection": "close" 
    }

    # --- LÓGICA DE REINTENTOS ---
    for intento in range(3):
        try:
            print(f"⏳ Intento {intento + 1}/3 - Conectando con Foursquare...")
            # Timeout de 60s por la latencia detectada
            response = requests.get(url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            return [_normalize_foursquare_place(p) for p in results]

        except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError):
            print(f"⚠️ La conexión se cortó. Reintentando...")
            continue 
        except requests.exceptions.Timeout:
            print(f"⚠️ El tiempo de espera se agotó. Reintentando...")
            continue
        except requests.exceptions.RequestException as e:
            # Si el error es 401 (llave mal) o 400, no tiene caso reintentar
            print(f"❌ Error fatal en la petición: {e}")
            break
            
    return []

def _normalize_foursquare_place(fsq_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapea la respuesta de Foursquare al modelo interno 'Place'
    """
    return {
        "name": fsq_data.get("name"),
        "address": fsq_data.get("location", {}).get("formatted_address"),
        "rating": fsq_data.get("rating", 0),
        "place_id": fsq_data.get("fsq_id"),
        "types": [c.get("name") for c in fsq_data.get("categories", [])]
    }

if __name__ == "__main__":
    print("\n🚀 Probando el wrapper con tolerancia a fallos de red...")
    
    # Ciudad de prueba
    test_city = "Mexico City"
    test_category = "skatepark"
    
    lugares = search_places(test_city, test_category, limit=3)
    
    if lugares:
        print(f"✅ ¡LO LOGRAMOS! Se encontraron {len(lugares)} lugares:\n")
        for i, lugar in enumerate(lugares, 1):
            print(f"{i}. {lugar['name']}")
            print(f"   📍 Dirección: {lugar['address']}\n")
    else:
        print("\nEmpty: Después de 3 intentos, no se pudo obtener respuesta.")
        print("Revisa que tu .env tenga la clave 'GMAS...' y que no haya duplicados.")