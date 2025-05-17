import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


# Leer un archivo de calles y uno de POIs
calles = gpd.read_file("C:/Users/cmora/Downloads/DATA/STREETS_NAV/SREETS_NAV_4815096.geojson")
pois = pd.read_csv("C:/Users/cmora/Downloads/DATA/POIs/POI_4815098.csv")

# Ver primeras filas
#print(calles.head())
#print(pois.head())

#print("Columnas disponibles en calles:")
#print(calles.columns)
print("Columnas disponibles en POIs:")
print(pois.columns)


# Convertir calles a mapa
calles.plot(figsize=(10, 10))
