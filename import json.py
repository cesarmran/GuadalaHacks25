import geopandas as gpd

# Ruta al archivo (puede ser .geojson o .json si es geoespacial)
archivo = "C:/Users/52312/Downloads/Guadalahacks25/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815083.geojson"

# Leer el archivo
gdf = gpd.read_file(archivo)

# Mostrar las primeras filas
print(gdf.head())
gdf.to_csv("nav1.csv", index=False)

