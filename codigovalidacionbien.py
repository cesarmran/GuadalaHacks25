import requests
from shapely.geometry import Point
from shapely.ops import transform
import pyproj

# Para proyectar en metros
def proyectar(geom, from_epsg='EPSG:4326', to_epsg='EPSG:3857'):
    project = pyproj.Transformer.from_crs(from_epsg, to_epsg, always_xy=True).transform
    return transform(project, geom)

def buscar_poi_mas_cercano(nombre, lat, lon, radio_m=100):
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
        return None

    data = response.json()
    punto_central = proyectar(Point(lon, lat))
    resultados = []

    for elem in data['elements']:
        lat_poi = elem.get('lat') or elem.get('center', {}).get('lat')
        lon_poi = elem.get('lon') or elem.get('center', {}).get('lon')

        if lat_poi is not None and lon_poi is not None:
            punto_poi = proyectar(Point(lon_poi, lat_poi))
            distancia = punto_central.distance(punto_poi)

            resultados.append({
                'name': elem['tags'].get('name', 'Sin nombre'),
                'lat': lat_poi,
                'lon': lon_poi,
                'tipo': elem['type'],
                'id': elem['id'],
                'distancia_m': round(distancia, 2)
            })

    if not resultados:
        return None

    # Ordenar por distancia y devolver solo el más cercano
    resultados.sort(key=lambda x: x['distancia_m'])
    return resultados[0]

# Ejemplo de uso
nombre = "OXXO"
lat = 19.27056
lon = -99.6297
radio = 500  # metros

poi_cercano = buscar_poi_mas_cercano(nombre, lat, lon, radio)

if poi_cercano:
    print("✅ POI más cercano:")
    print(f"- {poi_cercano['name']} ({poi_cercano['lat']}, {poi_cercano['lon']})")
    print(f"🛣 Tipo: {poi_cercano['tipo']}, ID: {poi_cercano['id']}, Distancia: {poi_cercano['distancia_m']} m")
else:
    print("⚠ No se encontró ningún POI cercano.")
