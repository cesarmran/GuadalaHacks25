from shapely.geometry import LineString, Point
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from PIL import Image


# === Geometrías de ejemplo ===
linea = LineString([(-99.63421, 19.26966), (-99.63322, 19.27064)])
poi = Point(-99.641800, 19.270520)
porcentaje = 0.35

# === Determinar el lado del POI ===
def lado_del_poi(linea, poi_point, porcentaje):
    punto_linea = linea.interpolate(linea.length * porcentaje)
    punto_linea_siguiente = linea.interpolate(min(linea.length * (porcentaje + 0.01), linea.length))

    v = np.array([punto_linea_siguiente.x - punto_linea.x, punto_linea_siguiente.y - punto_linea.y])
    w = np.array([poi_point.x - punto_linea.x, poi_point.y - punto_linea.y])

    det = v[0]*w[1] - v[1]*w[0]

    if det > 0:
        return "izquierda"
    elif det < 0:
        return "derecha"
    else:
        return "sobre la línea"

lado = lado_del_poi(linea, poi, porcentaje)
print(f"El POI está a la {lado} de la línea.")

# === Bounding box del tile (ajústalo a tu tile real) ===
xmin = -99.64599609375
xmax = -99.635009765625
ymin = 19.269665296502325
ymax = 19.28003579627975

# === Cargar tile como imagen ===
tile = Image.open("/Users/ebonyvaladez/Desktop/data/docs/satellite_tile.png")

# === Crear GeoDataFrames ===
gdf_linea = gpd.GeoDataFrame(geometry=[linea], crs="EPSG:4326")
gdf_poi = gpd.GeoDataFrame(geometry=[poi], crs="EPSG:4326")

# === Graficar ===
fig, ax = plt.subplots(figsize=(8, 8))

# Mostrar tile como fondo (debe ajustarse al bbox)
ax.imshow(tile, extent=[xmin, xmax, ymin, ymax], origin='upper')

# Dibujar geometría
gdf_linea.plot(ax=ax, color='blue', linewidth=2, label='Línea')
gdf_poi.plot(ax=ax, color='red', markersize=80, label='POI')

plt.title("POI y línea sobre tile")
plt.xlabel("Longitud")
plt.ylabel("Latitud")
plt.legend()
plt.show()
