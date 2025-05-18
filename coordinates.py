import pandas as pd
import math

# Parámetros
input_csv = "C:/Users/52312/Downloads/Guadalahacks25/docs/merged_output4.csv"
geometry_column = "geometry"
target_percentage = 0.25  # Por ejemplo, 25% del camino

# Cargar el archivo CSV
df = pd.read_csv(input_csv)

# Función para calcular distancia Haversine en metros
def haversine(coord1, coord2):
    R = 6371000  # radio de la Tierra en metros
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# Listas para guardar resultados
total_distances = []
percent_lats = []
percent_lons = []

# Función principal para procesar la geometría
def process_linestring(wkt_string, percent):
    try:
        coords_raw = wkt_string.replace("LINESTRING", "").replace("(", "").replace(")", "").strip()
        coords_list = [tuple(map(float, coord.split()))[::-1] for coord in coords_raw.split(",")]

        # Detectar inicio y fin basado en latitud, luego longitud
        start = max(coords_list, key=lambda c: (c[0], -c[1]))
        end = min(coords_list, key=lambda c: (c[0], -c[1]))

        # Calcular distancia total y distancias individuales
        total_distance = 0
        distances = []
        for i in range(len(coords_list) - 1):
            dist = haversine(coords_list[i], coords_list[i + 1])
            distances.append(dist)
            total_distance += dist

        # Encontrar coordenada al porcentaje deseado
        target_distance = total_distance * percent
        accumulated = 0
        for i, d in enumerate(distances):
            accumulated += d
            if accumulated >= target_distance:
                point = coords_list[i + 1]
                return total_distance, point[0], point[1]

        # Si es 100%, devolver la última
        return total_distance, coords_list[-1][0], coords_list[-1][1]
    except Exception as e:
        print(f"Error processing geometry: {wkt_string}\n{e}")
        return None, None, None

# Procesar cada fila
for geom in df[geometry_column]:
    dist, lat, lon = process_linestring(geom, target_percentage)
    total_distances.append(dist)
    percent_lats.append(lat)
    percent_lons.append(lon)

# Agregar columnas al DataFrame
df["total_distance_m"] = total_distances
df["point_at_percent_lat"] = percent_lats
df["point_at_percent_lon"] = percent_lons

# Mostrar y guardar resultado
print(df[["total_distance_m", "point_at_percent_lat", "point_at_percent_lon"]].head())
df.to_csv("output_with_distances_1.csv", index=False)
