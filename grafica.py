import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import math

# Función para ubicar un POI sobre la calle
def ubicar_poi(linea, perc, lado, desplazamiento=0.0005):
    length = linea.length
    punto_base = linea.interpolate(perc * length)

    dx = linea.coords[-1][0] - linea.coords[0][0]
    dy = linea.coords[-1][1] - linea.coords[0][1]
    norm = math.sqrt(dx**2 + dy**2) if dx != 0 or dy != 0 else 1

    if lado == "L":
        offset = (-dy / norm * desplazamiento, dx / norm * desplazamiento)
    else:
        offset = (dy / norm * desplazamiento, -dx / norm * desplazamiento)

    return Point(punto_base.x + offset[0], punto_base.y + offset[1])

# Función para convertir coordenadas geográficas a pixeles en tile
def geo_to_pixel(lon, lat, bbox, tile_size=512):
    lon_min, lat_min, lon_max, lat_max = bbox
    x = (lon - lon_min) / (lon_max - lon_min) * tile_size
    y = (lat_max - lat) / (lat_max - lat_min) * tile_size  # eje y invertido
    return round(x), round(y)

ruta_calles = "/Users/ebonyvaladez/Desktop/data/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815441.geojson"
ruta_pois = "/Users/ebonyvaladez/Desktop/data/POIs/POI_4815441.csv"

# Bounding box del tile (ajústalo a tu zona de interés)
bbox = (-99.3, 19.2, -99.0, 19.5)  # (lon_min, lat_min, lon_max, lat_max)

# Cargar datos
calles = gpd.read_file(ruta_calles)
pois = pd.read_csv(ruta_pois)

# Filtrar POIs válidos
pois_validos = pois[pois["LINK_ID"].isin(calles["link_id"])]
poi = pois_validos.iloc[0]

# Obtener geometría del link
link_geom = calles[calles["link_id"] == poi["LINK_ID"]].geometry.values[0]
perc = poi["PERCFRREF"]
lado = poi["POI_ST_SD"]
poi_geom = ubicar_poi(link_geom, perc, lado)

# Obtener coordenadas geográficas
lon = poi_geom.x
lat = poi_geom.y

# Convertir a coordenadas en pixeles
x_px, y_px = geo_to_pixel(lon, lat, bbox)

# Imprimir resultados
print("Coordenadas del POI:")
print(f"Longitud (x): {lon}")
print(f"Latitud  (y): {lat}")
print("Coordenadas en tile 512x512 px:")
print(f"x: {x_px} px")
print(f"y: {y_px} px")
