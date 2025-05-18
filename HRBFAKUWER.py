import pandas as pd
import math
import requests
import pickle
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import os

# ---------------- CONFIGURACIÓN ----------------
nav_path = "/Users/ebonyvaladez/Desktop/data/output_with_dynamic_percentages.csv"
poi_path = "/Users/ebonyvaladez/Desktop/data/POIs/POI_4815075.csv"
output_path = "/Users/ebonyvaladez/Desktop/Ebonysss/GuadalaHacks25/output.csv"
cache_path = "cache_overpass.pkl"
radio_m = 500

# ---------------- FUNCIONES AUXILIARES ----------------
def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
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

def buscar_pois(nombre, lat, lon, radio_m=100, intentos=3):
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
    for intento in range(intentos):
        try:
            r = requests.post(url, data=query, headers=headers, timeout=25)
            if r.status_code == 200:
                data = r.json()
                nombres = [e['tags'].get('name', 'N/A') for e in data.get('elements', []) if 'tags' in e]
                return "; ".join(nombres) if nombres else "No encontrado"
        except Exception:
            continue
    return "Error"

# ---------------- MAIN ----------------
nav_df = pd.read_csv(nav_path)
poi_df = pd.read_csv(poi_path)

nav_df.columns = nav_df.columns.str.lower()
poi_df.columns = poi_df.columns.str.lower()

# Verifica que exista 'percfrref'
if "percfrref" not in nav_df.columns:
    raise ValueError("Falta la columna 'percfrref' en nav_df")

# Normaliza a decimal entre 0 y 1
nav_df["percent_decimal"] = nav_df["percfrref"] / 100.0

# Nombre del POI
nombre_col = "poi_name"
if nombre_col not in poi_df.columns:
    poi_df[nombre_col] = poi_df["poi_id"]

# Fusión
merged = pd.merge(nav_df[['link_id', 'geometry', 'percent_decimal']],
                  poi_df[['link_id', 'poi_id', nombre_col]],
                  on='link_id', how='inner')

# Calcular coordenadas en la línea
total_distances, percent_lats, percent_lons = [], [], []
for _, row in merged.iterrows():
    porcentaje = row["percent_decimal"]
    dist, lat, lon = process_linestring(row["geometry"], porcentaje)
    total_distances.append(dist)
    percent_lats.append(lat)
    percent_lons.append(lon)

merged["total_distance_m"] = total_distances
merged["percent_lat"] = percent_lats
merged["percent_lon"] = percent_lons

# Cargar cache si existe
if os.path.exists(cache_path):
    with open(cache_path, "rb") as f:
        cache = pickle.load(f)
else:
    cache = {}

def consulta(row):
    lat, lon = row["percent_lat"], row["percent_lon"]
    nombre = str(row[nombre_col])
    key = (nombre, lat, lon)
    if pd.isna(lat) or pd.isna(lon):
        return ""
    if key in cache:
        return cache[key]
    resultado = buscar_pois(nombre, lat, lon, radio_m)
    cache[key] = resultado
    return resultado

# Ejecutar en paralelo
rows = merged.to_dict("records")
with ThreadPoolExecutor(max_workers=5) as executor:
    resultados = list(tqdm(executor.map(consulta, rows), total=len(rows), desc="Consultando POIs"))

merged["pois_encontrados"] = resultados

# Guardar resultados y cache
with open(cache_path, "wb") as f:
    pickle.dump(cache, f)
resultados = list(tqdm(executor.map(consulta, rows), total=len(rows), desc="Consultando POIs"))

merged.to_csv(output_path, index=False)
print(f"✅ Archivo guardado en {output_path}")
