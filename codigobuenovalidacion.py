import requests

def buscar_poi_con_overpass(nombre, lat, lon, radio_m=100):
    """
    Busca POIs por nombre dentro de un radio usando Overpass API.
    """
    query = f"""
    [out:json][timeout:25];
    (
      node["name"~"{nombre}", i](around:{radio_m},{lat},{lon});
      way["name"~"{nombre}", i](around:{radio_m},{lat},{lon});
      relation["name"~"{nombre}", i](around:{radio_m},{lat},{lon});
    );
    out center;
    """

    url = "https://overpass-api.de/api/interpreter"
    headers = {'User-Agent': 'POIRadiusChecker/1.0 (tucorreo@ejemplo.com)'}

    response = requests.post(url, data=query, headers=headers)

    if response.status_code != 200:
        print("❌ Error en Overpass:", response.status_code)
        return []

    data = response.json()

    resultados = []
    for elem in data['elements']:
        if 'tags' in elem and 'name' in elem['tags']:
            nombre_poi = elem['tags']['name']
            lat_poi = elem.get('lat') or elem.get('center', {}).get('lat')
            lon_poi = elem.get('lon') or elem.get('center', {}).get('lon')

            if lat_poi is not None and lon_poi is not None:
                resultados.append({
                    'name': nombre_poi,
                    'lat': lat_poi,
                    'lon': lon_poi,
                    'tipo': elem['type'],
                    'id': elem['id']
                })

    return resultados

# Ejemplo de uso
nombre = "INSTITUTO CENCA"
lat = 19.27045
lon = -99.62957
radio = 100  # metros

resultados = buscar_poi_con_overpass(nombre, lat, lon, radio)

if not resultados:
    print("No se encontró nada en ese radio.")
else:
    print(f"Encontrados {len(resultados)} resultados cerca de ({lat}, {lon})")
    for r in resultados:
        print(f"- {r['name']} ({r['lat']}, {r['lon']})")



