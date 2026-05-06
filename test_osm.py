import time

import requests

LUGARES_PRUEBA = {
    "Paris (Centro)": {"lat": 48.8584, "lon": 2.2945},
    "CDMX (Zocalo)": {"lat": 19.4326, "lon": -99.1332},
}


def probar_overpass_optimizado(nombre_lugar, lat, lon, categoria):
    print(f"\n{'=' * 50}")
    print(f"🚀 PRUEBA PARA: {nombre_lugar} | Categoría: {categoria.upper()}")

    url = "https://overpass-api.de/api/interpreter"

    # 1. Usamos 'nw' (Node y Way). Adiós a las Relations.
    # 2. Radio de 3000m (súper rápido, cubre el centro de la ciudad).
    # 3. Exigimos "wikidata" para popularidad global.
    if categoria == "cultura":
        nodos_query = f"""
          nw(around:3000, {lat}, {lon})["tourism"="museum"]["wikidata"];
          nw(around:3000, {lat}, {lon})["tourism"="gallery"]["wikidata"];
        """
    elif categoria == "destacados":
        nodos_query = f"""
          nw(around:3000, {lat}, {lon})["tourism"="attraction"]["wikidata"];
          nw(around:3000, {lat}, {lon})["historic"="monument"]["wikidata"];
        """

    query = f"""
    [out:json][timeout:15];
    (
    {nodos_query}
    );
    out 15 center tags;
    """

    try:
        start_time = time.time()
        headers = {
            "User-Agent": "Datamundi-CityLens/1.0 (estudiante@sistemas.edu)",
            "Accept": "*/*",
        }

        response = requests.post(url, data={"data": query}, headers=headers, timeout=20)

        tiempo_total = round(time.time() - start_time, 2)
        print(f"⏱️  Tiempo: {tiempo_total} seg | 📡 Status HTTP: {response.status_code}")

        response.raise_for_status()
        datos = response.json()
        elementos = datos.get("elements", [])

        print(
            f"✅ Se encontraron {len(elementos)} lugares populares (Nodos y Edificios)."
        )

        for i, el in enumerate(elementos, 1):
            nombre = el.get("tags", {}).get("name", "Sin nombre")
            tipo_osm = el.get("type", "desconocido")

            print(f"  {i}. [{tipo_osm.upper()}] {nombre}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    print("Iniciando Prueba Definitiva OSM (NW + Wikidata + 3km)...\n")

    # Probamos CDMX - Cultura
    probar_overpass_optimizado(
        "CDMX (Zocalo)",
        LUGARES_PRUEBA["CDMX (Zocalo)"]["lat"],
        LUGARES_PRUEBA["CDMX (Zocalo)"]["lon"],
        "cultura",
    )
    time.sleep(2)

    # Probamos Paris - Cultura
    probar_overpass_optimizado(
        "Paris (Centro)",
        LUGARES_PRUEBA["Paris (Centro)"]["lat"],
        LUGARES_PRUEBA["Paris (Centro)"]["lon"],
        "cultura",
    )
