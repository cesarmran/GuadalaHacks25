import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import math

# Función para ubicar un POI en un lado de la calle con desplazamiento lateral
def ubicar_poi(linea, perc, lado, desplazamiento=0.0005):
    length = linea.length
    punto_base = linea.interpolate(perc * length)

    dx = linea.coords[-1][0] - linea.coords[0][0]
    dy = linea.coords[-1][1] - linea.coords[0][1]
    norm = math.sqrt(dx**2 + dy**2) if dx != 0 or dy != 0 else 1

    if lado == "L":
        offset = (-dy / norm * desplazamiento, dx / norm * desplazamiento)
    else:
        offset = (dy / norm * desplazamiento, -dx / norm * desplazamiento)

    return Point(punto_base.x + offset[0], punto_base.y + offset[1])

# Función para graficar una calle con su POI
def graficar_poi(poi, calles):
    link_id = poi["LINK_ID"]
    perc = poi["PERCFRREF"]
    lado = poi["POI_ST_SD"]

    if link_id not in calles["link_id"].values:
        print(f"❌ LINK_ID {link_id} no encontrado en dataset de calles.")
        return

    # Obtener la geometría del link
    linea = calles[calles["link_id"] == link_id].geometry.values[0]
    ref_node = Point(linea.coords[0])
    nonref_node = Point(linea.coords[-1])
    poi_geom = ubicar_poi(linea, perc, lado)
    

    # Imprimir coordenadas
    print(f"📍 Coordenadas del POI (lado {lado}):")
    print(f"Longitud (x): {poi_geom.x}")
    print(f"Latitud  (y): {poi_geom.y}")

    # Graficar
    x, y = linea.xy
    plt.plot(x, y, color='black', label="Calle (Link)")

    plt.scatter(ref_node.x, ref_node.y, color='blue', label="Reference Node")
    plt.scatter(nonref_node.x, nonref_node.y, color='orange', label="Non-Reference Node")
    plt.scatter(poi_geom.x, poi_geom.y, color='green', s=80, label=f'POI {lado}')

    plt.title(f"POI sobre calle\nPOI_ID: {poi['POI_ID']} | LINK_ID: {link_id}")
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.show()

# 🛠 AJUSTA ESTAS RUTAS A TU COMPUTADORA
ruta_calles = "/Users/ebonyvaladez/Desktop/data/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815441.geojson"
ruta_pois = "/Users/ebonyvaladez/Desktop/data/POIs/POI_4815441.csv"

# Cargar datos
calles = gpd.read_file(ruta_calles)
pois = pd.read_csv(ruta_pois)

# Filtrar POIs con LINK_ID válido
pois_validos = pois[pois["LINK_ID"].isin(calles["link_id"])]

# Seleccionar uno (o cambiar el índice)
poi = pois_validos.iloc[0]

# Ejecutar visualización
graficar_poi(poi, calles)
