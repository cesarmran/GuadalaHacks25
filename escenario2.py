import pandas as pd
import math
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# ---------------- CONFIGURACIÓN ----------------
nav_path = "C:/Users/cmora/Documents/GuadalaHacks25/output_with_dynamic_percentages.csv"
poi_path = "C:/Users/cmora/Downloads/DATA/POIs/POI_4815075.csv"
output_path = "C:/Users/cmora/Documents/Guadalahacks25/output.csv"
target_percentage = 0.25  # puedes cambiarlo
radio_m = 500  # radio de búsqueda para Overpass

# ---------------- FUNCIONES ----------------

def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def process_linestring(wkt_string, percent):
    try:
        coords_raw = wkt_string.replace("LINESTRING", "").replace("(", "").replace(")", "").strip()
        coords_list = [tuple(map(float, c.split()))[::-1] for c in coords_raw.split(",")]
        total_distance = sum(haversine(coords_list[i], coords_list[i+1]) for i in range(len(coords_list)-1))
        target_distance = total_distance * percent
        accumulated = 0
        for i in range(len(coords_list) - 1):
            d = haversine(coords_list[i], coords_list[i+1])
            accumulated += d
            if accumulated >= target_distance:
                return total_distance, coords_list[i + 1][0], coords_list[i + 1][1]
        return total_distance, coords_list[-1][0], coords_list[-1][1]
    except:
        return None, None, None

def buscar_pois(nombre, lat, lon, radio_m=100):
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
    try:
        response = requests.post(url, data=query, headers=headers, timeout=25)
        if response.status_code != 200:
            return "No encontrado"
        data = response.json()
        nombres = [e['tags'].get('name', 'N/A') for e in data.get('elements', []) if 'tags' in e]
        return "; ".join(nombres) if nombres else "No encontrado"
    except:
        return "Error"

# ---------------- 1. FUSIÓN DE ARCHIVOS ----------------

nav_df = pd.read_csv(nav_path)
poi_df = pd.read_csv(poi_path)

nav_df.columns = nav_df.columns.str.lower()
poi_df.columns = poi_df.columns.str.lower()

# CAMBIA ESTA LÍNEA si tienes otro nombre de columna que representa el nombre del POI
nombre_columna = "poi_name"  # <-- cámbiala si tienes otro nombre
if nombre_columna not in poi_df.columns:
    poi_df[nombre_columna] = poi_df["poi_id"]  # fallback a poi_id si no tienes nombre real



merged = pd.merge(nav_df[['link_id', 'geometry']],
                 poi_df[['link_id', 'poi_id', nombre_columna]],
                  on='link_id', how='inner')

merged = merged.head(50)  # solo las primeras 20 filas
# ---------------- 2. CALCULAR COORDENADAS ----------------

total_distances = []
percent_lats = []
percent_lons = []

for geom in merged["geometry"]:
    dist, lat, lon = process_linestring(geom, target_percentage)
    total_distances.append(dist)
    percent_lats.append(lat)
    percent_lons.append(lon)

merged["total_distance_m"] = total_distances
merged["percent_lat"] = percent_lats
merged["percent_lon"] = percent_lons

# ---------------- 3. CONSULTAR OVERPASS EN PARALELO ----------------

cache = {}

def consulta_con_cache(row):
    lat, lon = row["percent_lat"], row["percent_lon"]
    nombre = str(row[nombre_columna])
    key = (nombre, lat, lon)
    if pd.isna(lat) or pd.isna(lon):
        return ""
    if key in cache:
        return cache[key]
    resultado = buscar_pois(nombre, lat, lon, radio_m)
    cache[key] = resultado
    return resultado

rows = list(merged.to_dict("records"))
results = [None] * len(rows)

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(consulta_con_cache, row): i for i, row in enumerate(rows)}
    for future in tqdm(as_completed(futures), total=len(futures), desc="Consultando POIs"):
        i = futures[future]
        try:
            results[i] = future.result()
        except Exception:
            results[i] = "Error"

merged["pois_encontrados"] = results

# ---------------- 4. EXPORTAR ----------------

merged.to_csv(output_path, index=False)
print(f"✅ Proceso completo. Archivo guardado en: {output_path}")
