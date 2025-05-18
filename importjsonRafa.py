import geopandas as gpd

# Ruta al archivo (puede ser .geojson o .json si es geoespacial)
archivo = "C:/Users/cmora/Downloads/DATA/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815075.geojson"

# Leer el archivo
gdf = gpd.read_file(archivo)

# Mostrar las primeras filas
print(gdf.head())
gdf.to_csv("C:/Users/cmora/Documents/GuadalaHacks25/nav2.csv", index=False)