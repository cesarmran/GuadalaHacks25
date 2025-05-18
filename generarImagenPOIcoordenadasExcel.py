import pandas as pd
import requests
import math
import os
import matplotlib.pyplot as plt
from PIL import Image
from shapely.geometry import LineString
import geopandas as gpd

# ---------------------------------------
# Funciones base de coordenadas y tiles
# ---------------------------------------
geojson_folder = 'C:/Users/cmora/Downloads/DATA/STREETS_NAV'

def lat_lon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    n = 2.0 ** zoom
    x = int((lon_rad - (-math.pi)) / (2 * math.pi) * n)
    y = int((1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n)
    return (x, y)

def tile_coords_to_lat_lon(x, y, zoom):
    n = 2.0 ** zoom
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

def get_tile_bounds(x, y, zoom):
    lat1, lon1 = tile_coords_to_lat_lon(x, y, zoom)
    lat2, lon2 = tile_coords_to_lat_lon(x + 1, y, zoom)
    lat3, lon3 = tile_coords_to_lat_lon(x + 1, y + 1, zoom)
    lat4, lon4 = tile_coords_to_lat_lon(x, y + 1, zoom)
    return (lat1, lon1), (lat2, lon2), (lat3, lon3), (lat4, lon4)

def create_wkt_polygon(bounds):
    (lat1, lon1), (lat2, lon2), (lat3, lon3), (lat4, lon4) = bounds
    wkt = f"POLYGON(({lon1} {lat1}, {lon2} {lat2}, {lon3} {lat3}, {lon4} {lat4}, {lon1} {lat1}))"
    return wkt

# ---------------------------------------
# Función para obtener y guardar imagen
# ---------------------------------------

def get_satellite_tile(lat, lon, zoom, tile_format, tile_size, api_key, output_path, filename_prefix):
    x, y = lat_lon_to_tile(lat, lon, zoom)

    url = f'https://maps.hereapi.com/v3/base/mc/{zoom}/{x}/{y}/{tile_format}&style=satellite.day&size={tile_size}?apiKey={api_key}'

    response = requests.get(url)

    if response.status_code == 200:
        filepath = os.path.join(output_path, f'{filename_prefix}.{tile_format}')
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f'✅ Tile saved: {filepath}')
    else:
        print(f'❌ Failed to retrieve tile for {filename_prefix}. Status: {response.status_code}')

    bounds = get_tile_bounds(x, y, zoom)
    return create_wkt_polygon(bounds)

# Funciones auxiliares para dibujo
# Función corregida para convertir lat/lon a píxeles
def geo_to_pixel(lat, lon, lat_min, lon_min, lat_max, lon_max, width, height):
    px = (lon - lon_min) / (lon_max - lon_min) * width
    py = (lat_max - lat) / (lat_max - lat_min) * height
    return px, py


def buscar_link_en_geojsons(link_id):
    for file in os.listdir(geojson_folder):
        if file.endswith(".geojson"):
            gdf = gpd.read_file(os.path.join(geojson_folder, file))
            if str(link_id) in gdf['link_id'].astype(str).values:
                return gdf[gdf['link_id'].astype(str) == str(link_id)].geometry.values[0]
    return None

# ---------------------------------------
# PARTE PRINCIPAL: Leer CSV y procesar
# ---------------------------------------

# Configuración
api_key = 'iQPGr-iOp1v3ZbkoCmVCX2T2B91QQziGAz4uD5fax7o'
zoom_level = 17
tile_size = 512
tile_format = 'png'
ruta_csv = 'C:/Users/cmora/Documents/sat_tiles/pois_con_coordenadas.csv'
carpeta_salida = 'C:/Users/cmora/Documents/sat_tiles/'

# Crear carpeta si no existe
os.makedirs(carpeta_salida, exist_ok=True)

# Leer datos
df = pd.read_csv(ruta_csv)

assert {'POI_ID', 'LINK_ID', 'LAT', 'LON'}.issubset(df.columns), "El archivo debe tener columnas: POI_ID, LINK_ID, LAT, LON"

# Procesar cada POI
for _, row in df.iterrows():
    poi_id = int(row['POI_ID'])
    lat = row['LAT']
    lon = row['LON']
    nombre_archivo = f"sat_poi_{poi_id}"
    wkt = get_satellite_tile(lat, lon, zoom_level, tile_format, tile_size, api_key, carpeta_salida, nombre_archivo)
    print(f"📍 WKT Bounds for POI {poi_id}: {wkt}")

    # Agregar punto y línea a la imagen
    imagen_path = os.path.join(carpeta_salida, f'{nombre_archivo}.{tile_format}')
    if os.path.exists(imagen_path):
        img = Image.open(imagen_path)
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(img)

        x_tile, y_tile = lat_lon_to_tile(lat, lon, zoom_level)
        (lat1, lon1), (_, _), (lat2, lon2), (_, _) = get_tile_bounds(x_tile, y_tile, zoom_level)

        px, py = geo_to_pixel(lat, lon, lat1, lon1, lat2, lon2, img.width, img.height)
        ax.plot(px, py, 'ro', markersize=5)

        link_id = row['LINK_ID']
        geom = buscar_link_en_geojsons(link_id)
        if isinstance(geom, LineString):
            coords = [geo_to_pixel(lat, lon, lat1, lon1, lat2, lon2, img.width, img.height)
                      for lon, lat in geom.coords]
            xs, ys = zip(*coords)
            ax.plot(xs, ys, color='cyan', linewidth=2)

        ax.axis('off')
        plt.savefig(imagen_path, bbox_inches='tight', pad_inches=0)
        plt.close()
