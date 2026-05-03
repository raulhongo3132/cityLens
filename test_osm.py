# test_osm.py
import json

import requests


def aislar_y_probar_overpass():
    """
    Script de diagnóstico de grado de ingeniería para probar la API de Overpass
    aislada de la arquitectura Flask.
    """
    # Coordenadas exactas que tenemos en tu base de datos para Santiago de Chile
    lat = -33.45
    lon = -70.67
    radio = 30000  # 30 kilómetros

    # Vamos a usar la etiqueta exacta de la categoría "cultura" que estaba fallando
    tag = '["tourism"="museum"]'

    # Construimos la consulta QL exacta que nuestro Wrapper debería estar generando
    query = f"""
    [out:json][timeout:25];
    (
      nwr{tag}["name"](around:{radio},{lat},{lon});
    );
    out body center 30;
    """

    print("🚀 Iniciando prueba aislada de Overpass API...")
    print(f"📡 Coordenadas: Lat {lat}, Lon {lon} (Santiago de Chile)")
    print(f"🔍 Etiqueta QL: {tag}")
    print("-" * 50)
    print("Enviando el siguiente bloque al motor alemán:")
    print(query)
    print("-" * 50)

    url = "https://overpass-api.de/api/interpreter"
    headers = {"User-Agent": "CityLens_Sandbox_Test/1.0"}

    try:
        response = requests.post(
            url, data=query.encode("utf-8"), headers=headers, timeout=30
        )

        print(f"📥 Código HTTP de respuesta: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            elementos = data.get("elements", [])
            print(f"📦 Total de elementos crudos devueltos: {len(elementos)}")

            # Guardamos la evidencia en un archivo local para que la puedas inspeccionar a fondo
            with open("osm_evidencia.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("✅ El JSON completo ha sido guardado en 'osm_evidencia.json'")

            # Mostramos un extracto del primer elemento si existe
            if elementos:
                print("\n👀 Muestra del primer elemento (Data Cruda):")
                primer_elemento = {
                    "id": elementos[0].get("id"),
                    "type": elementos[0].get("type"),
                    "name": elementos[0].get("tags", {}).get("name"),
                    "tags": elementos[0].get("tags", {}),
                }
                print(json.dumps(primer_elemento, indent=2, ensure_ascii=False))
            else:
                print(
                    "\n⚠️ ALERTA: La API respondió con éxito (200 OK), pero el arreglo 'elements' está vacío []."
                )
                print(
                    "Esto significa que la sintaxis QL o la geografía fallaron desde la fuente, no en nuestro Backend."
                )

        else:
            print(f"❌ La API rechazó la solicitud: {response.text}")

    except Exception as e:
        print(f"🚨 Error crítico de conexión: {e}")


if __name__ == "__main__":
    aislar_y_probar_overpass()
