import geopandas as gpd
import pandas as pd
import math
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from shapely.geometry import Point, LineString
import numpy as np

# Ruta al archivo (puede ser .geojson o .json si es geoespacial) NAMING
archivo = "C:/Users/52312/Downloads/Guadalahacks25/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815075.geojson"

# Leer el archivo
file1 = gpd.read_file(archivo)
file2 = pd.read_csv("C:/Users/52312/Downloads/Guadalahacks25/POIs/POI_4815075.csv")



# Load the CSV files
file1.columns = file1.columns.str.lower()
file2.columns = file2.columns.str.lower()
# Define the common column and the columns to extract
common_column = "link_id"
file1_column = "geometry"
file2_column = "poi_id" 
file2_column1 = "percfrref"
file2_column2 = "poi_name"


# Merge the files based on the common column
merged = pd.merge(file1[[common_column, file1_column]],
                  file2[[common_column, file2_column, file2_column1, file2_column2]],
                  on=common_column,
                  how='inner')  # or 'left', 'right', 'outer' depending on what you want



# Parámetros
merged=merged.head(300)
df = merged

geometry_column = "geometry"
percentage_column = "percfrref"  # ← nombre real de la columna con porcentaje

# Haversine en metros
def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# Interpolación lineal
def interpolate(coord1, coord2, t):
    lat = coord1[0] + t * (coord2[0] - coord1[0])
    lon = coord1[1] + t * (coord2[1] - coord1[1])
    return (lat, lon)

# Procesar geometría y porcentaje
def process_linestring(wkt_string, percent_int):
    try:
        percent = percent_int / 100.0  # convertir entero a decimal
        coords_raw = wkt_string.replace("LINESTRING", "").replace("(", "").replace(")", "").strip()
        coords_list = [tuple(map(float, coord.split()))[::-1] for coord in coords_raw.split(",")]

        # Detectar dirección por latitud y longitud
        start = max(coords_list, key=lambda c: (c[0], -c[1]))
        end = min(coords_list, key=lambda c: (c[0], -c[1]))

        # Calcular distancias entre tramos
        total_distance = 0
        segment_distances = []
        for i in range(len(coords_list) - 1):
            d = haversine(coords_list[i], coords_list[i + 1])
            segment_distances.append(d)
            total_distance += d

        # Encontrar coordenada al porcentaje deseado
        target_distance = total_distance * percent
        accumulated = 0
        for i, d in enumerate(segment_distances):
            if accumulated + d >= target_distance:
                overshoot = target_distance - accumulated
                t = overshoot / d
                point = interpolate(coords_list[i], coords_list[i + 1], t)
                return total_distance, point[0], point[1]
            accumulated += d

        return total_distance, coords_list[-1][0], coords_list[-1][1]
    except Exception as e:
        print(f"Error processing geometry:\n{wkt_string}\n{e}")
        return None, None, None

# Listas de salida
total_distances = []
percent_lats = []
percent_lons = []

for i, row in df.iterrows():
    geom = row[geometry_column]
    perc = row[percentage_column]

    if pd.isna(perc) or not isinstance(perc, (int, float)):
        total_distances.append(None)
        percent_lats.append(None)
        percent_lons.append(None)
        continue

    dist, lat, lon = process_linestring(geom.wkt, perc)
    total_distances.append(dist)
    percent_lats.append(lat)
    percent_lons.append(lon)


# Guardar en el DataFrame
df["total_distance_m"] = total_distances
df["point_at_percent_lat"] = percent_lats
df["point_at_percent_lon"] = percent_lons

# Exportar resultado
print(df[["percfrref", "total_distance_m", "point_at_percent_lat", "point_at_percent_lon"]].head())

def lado_del_poi(linea, poi_point, porcentaje):
    p1 = linea.interpolate(linea.length * porcentaje)
    delta = 0.01
    p2 = linea.interpolate(min(linea.length * (porcentaje + delta), linea.length))
    v = np.array([p2.x - p1.x, p2.y - p1.y])
    w = np.array([poi_point.x - p1.x, poi_point.y - p1.y])
    det = v[0] * w[1] - v[1] * w[0]
    if det > 0:
        return "izquierda"
    elif det < 0:
        return "derecha"
    else:
        return "sobre la línea"

# === Rutas a tus archivos ===
ruta_pois = df
ruta_lineas = archivo
output_path = "C:/Users/52312/Downloads/Guadalahacks25/POIs/caso2final.csv"

# === CARGAR ARCHIVOS ===
df_pois = df.copy()
df_pois.columns = df_pois.columns.str.lower()
gdf_lineas = gpd.read_file(ruta_lineas)
gdf_lineas.columns = gdf_lineas.columns.str.lower()

# === CONFIGURACIÓN DE COLUMNAS ===
lat_col = "point_at_percent_lat"
lon_col = "point_at_percent_lon"
perc_col = "percfrref"
link_col = "link_id"

# Normaliza el porcentaje a 0–1
df_pois["porcentaje"] = df_pois[perc_col] / 100

# GeoDataFrame de POIs
gdf_pois = gpd.GeoDataFrame(
    df_pois,
    geometry=gpd.points_from_xy(df_pois[lon_col], df_pois[lat_col]),
    crs="EPSG:4326"
)

# Renombra la geometría de líneas para evitar colisión con la del POI
gdf_lineas = gdf_lineas.rename(columns={"geometry": "geometry_linea"})

# Merge con geometría renombrada
combinados = gdf_pois.merge(gdf_lineas[[link_col, "geometry_linea"]], on=link_col, how="left")

# Cálculo de lado
def calcular_lado(row):
    if pd.isnull(row["geometry_linea"]):
        return "sin_linea"
    return lado_del_poi(row["geometry_linea"], row["geometry"], row["porcentaje"])

combinados["lado"] = combinados.apply(calcular_lado, axis=1)

# Guardar CSV (sin geometría si no la necesitas)
combinados.drop(columns=["geometry", "geometry_linea"]).to_csv(output_path, index=False)
print(f"✅ Listo. Archivo guardado en: {output_path}")

