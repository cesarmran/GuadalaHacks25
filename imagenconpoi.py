import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import math
import numpy as np
from skimage.color import rgb2gray
from skimage.filters import threshold_otsu

# === CONFIGURACIÓN ===
ruta_pois = "/Users/ebonyvaladez/Desktop/data/POIs/POI_4815075.csv"
ruta_calles = "/Users/ebonyvaladez/Desktop/data/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815075.geojson"
ruta_imagen = "/Users/ebonyvaladez/Desktop/data/docs/satellite_tile.png"



# Bounding box del tile (coordenadas geográficas)
bbox = (
    -99.64599609375,         # lon_min
    19.269665296502325,      # lat_min
    -99.635009765625,        # lon_max
    19.28003579627975        # lat_max
)


tile_size = 512  # tamaño en píxeles

# === FUNCIONES ===

def geo_to_pixel(lon, lat, bbox, tile_size=512):
    lon_min, lat_min, lon_max, lat_max = bbox
    x = (lon - lon_min) / (lon_max - lon_min) * tile_size
    y = (lat_max - lat) / (lat_max - lat_min) * tile_size
    return int(x), int(y)

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

# === CARGA DE DATOS ===

calles = gpd.read_file(ruta_calles)
pois = pd.read_csv(ruta_pois)
pois_validos = pois[pois["LINK_ID"].isin(calles["link_id"])]
id_seleccionado = 1296526969  # <--- cambia este valor
poi = pois_validos[pois_validos["POI_ID"] == id_seleccionado].iloc[0]

# Obtener la geometría del LINK
geom = calles[calles["link_id"] == poi["LINK_ID"]].geometry.values[0]
if geom.geom_type == "MultiLineString":
    linea = list(geom.geoms)[0]
else:
    linea = geom

# Ubicar el POI
poi_geom = ubicar_poi(linea, poi["PERCFRREF"], poi["POI_ST_SD"])
x_poi, y_poi = geo_to_pixel(poi_geom.x, poi_geom.y, bbox, tile_size)

# Obtener coordenadas de la línea y convertirlas a píxeles
line_coords = list(linea.coords)
line_pixels = [geo_to_pixel(x, y, bbox, tile_size) for x, y in line_coords]
x_line, y_line = zip(*line_pixels)

# Procesar imagen y binarizar
imagen = Image.open(ruta_imagen).convert("RGB")
img_np = np.array(imagen)
gray = rgb2gray(img_np)
thresh = threshold_otsu(gray)
binary = gray < thresh

# === VISUALIZAR ===
plt.figure(figsize=(6, 6))
plt.imshow(binary, cmap='gray')
plt.plot(x_line, y_line, color='cyan', linewidth=2, label="LINK (calle)")
plt.scatter(x_poi, y_poi, color='red', s=60, label="POI")
plt.title("POI y LINK sobre imagen binarizada")
plt.axis("off")
plt.legend()
plt.tight_layout()
plt.show()

# === IMPRIMIR ID DEL POI Y LINK ===
print(f"\nID del POI: {poi['POI_ID'] if 'POI_ID' in poi else poi.name}")
print(f"LINK_ID asociado: {poi['LINK_ID']}")
