import geopandas as gpd

# Ruta al archivo (puede ser .geojson o .json si es geoespacial)
archivo = "STREETS_NAV\\SREETS_NAV_4815075.geojson"

# Leer el archivo
gdf = gpd.read_file(archivo)

# Mostrar las primeras filas
print(gdf.head())

# Guardar como CSV
gdf.to_csv("streets_nav_output.csv", index=False)

