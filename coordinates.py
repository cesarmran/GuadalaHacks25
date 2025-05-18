import pandas as pd
import math

# Parámetros
input_csv = "C:/Users/52312/Downloads/Guadalahacks25/docs/merged_output4.csv"
geometry_column = "geometry"
percentage_column = "percfrref"  # ← nombre real de la columna con porcentaje

# Cargar CSV
df = pd.read_csv(input_csv)

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

# Procesar fila por fila
for i, row in df.iterrows():
    geom = row[geometry_column]
    perc = row[percentage_column]
    dist, lat, lon = process_linestring(geom, perc)
    total_distances.append(dist)
    percent_lats.append(lat)
    percent_lons.append(lon)

# Guardar en el DataFrame
df["total_distance_m"] = total_distances
df["point_at_percent_lat"] = percent_lats
df["point_at_percent_lon"] = percent_lons

# Exportar resultado
print(df[["percfrref", "total_distance_m", "point_at_percent_lat", "point_at_percent_lon"]].head())
df.to_csv("output_with_dynamic_percentages.csv", index=False)
