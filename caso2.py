import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import numpy as np

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
ruta_pois = "/Users/ebonyvaladez/Desktop/data/output_with_dynamic_percentages.csv"
ruta_lineas = "/Users/ebonyvaladez/Desktop/data/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815075.geojson"  # puede ser .geojson o .shp
output_path = "/Users/ebonyvaladez/Desktop/data/output_con_lado.csv"

# === CARGAR ARCHIVOS ===
df_pois = pd.read_csv(ruta_pois)
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
merged = gdf_pois.merge(gdf_lineas[[link_col, "geometry_linea"]], on=link_col, how="left")

# Cálculo de lado
def calcular_lado(row):
    if pd.isnull(row["geometry_linea"]):
        return "sin_linea"
    return lado_del_poi(row["geometry_linea"], row["geometry"], row["porcentaje"])

merged["lado"] = merged.apply(calcular_lado, axis=1)

# Guardar CSV (sin geometría si no la necesitas)
merged.drop(columns=["geometry", "geometry_linea"]).to_csv(output_path, index=False)
print(f"✅ Listo. Archivo guardado en: {output_path}")