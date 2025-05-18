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
nombre = "Accesorios Chino"
lat = 19.2710199
lon = -99.6422219
radio = 10  # metros

resultados = buscar_poi_con_overpass(nombre, lat, lon, radio)

if not resultados:
    print("⚠ No se encontró nada en ese radio.")
else:
    print(f"✅ Encontrados {len(resultados)} resultados cerca de ({lat}, {lon})")
    for r in resultados:
        print(f"- {r['name']} ({r['lat']}, {r['lon']}) – {r['tipo']} ID: {r['id']}")

import geopandas as gpd
from shapely.geometry import Point

# Supongamos que ya tienes:
gdf_links = gpd.read_file("/Users/ebonyvaladez/Desktop/data/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815075.geojson")  # o .shp
# - poi: coordenadas del POI
poi_coord = (-99.6418, 19.27052)
punto_poi = Point(poi_coord)

# Asegúrate de usar proyección en metros para calcular distancia real
gdf_links_proj = gdf_links.to_crs(epsg=3857)
punto_proj = gpd.GeoSeries([punto_poi], crs="EPSG:4326").to_crs(epsg=3857).iloc[0]

# Calcular la distancia a todas las calles
gdf_links_proj['dist_m'] = gdf_links_proj.distance(punto_proj)

# Obtener la calle más cercana
link_mas_cercano = gdf_links_proj.sort_values('dist_m').iloc[0]

print(f"📏 Distancia mínima: {link_mas_cercano['dist_m']:.2f} metros")
print(f"🛣 Link más cercano: {link_mas_cercano['link_id']}")
