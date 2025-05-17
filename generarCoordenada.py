import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt

def ubicar_poi(linea, perc, lado, desplazamiento=0.0005):
    length = linea.length
    punto_base = linea.interpolate(perc * length)
    
    dx = linea.coords[-1][0] - linea.coords[0][0]
    dy = linea.coords[-1][1] - linea.coords[0][1]
    norm = (dx**2 + dy**2)**0.5 if dx != 0 or dy != 0 else 1

    if lado == "L":
        offset = (-dy / norm * desplazamiento, dx / norm * desplazamiento)
    else:
        offset = (dy / norm * desplazamiento, -dx / norm * desplazamiento)

    return Point(punto_base.x + offset[0], punto_base.y + offset[1])

# 🛠️ AJUSTA ESTAS RUTAS A TU COMPUTADORA
ruta_pois = "C:/Users/cmora/Downloads/DATA/POIs/POI_4815098.csv"
ruta_calles = "C:/Users/cmora/Downloads/DATA/STREETS_NAV/SREETS_NAV_4815096.geojson"

# Cargar datos reales
pois = pd.read_csv(ruta_pois)
calles = gpd.read_file(ruta_calles)

# Buscar un POI que tenga su LINK_ID en las calles cargadas
pois_validos = pois[pois['LINK_ID'].isin(calles['link_id'])]    
poi = pois_validos.iloc[0]
link_geom = calles[calles['link_id'] == poi['LINK_ID']].geometry.values[0]

if calles[calles['link_id'] == poi['LINK_ID']].empty:
    print(f"No se encontró el LINK_ID {poi['LINK_ID']} en calles.")
else:
    link_geom = calles[calles['link_id'] == poi['LINK_ID']].geometry.values[0]


# Ubicar POI
poi_geom = ubicar_poi(link_geom, poi['PERCFRREF'], poi['POI_ST_SD'])


# Generar punto al lado contrario
lado_opuesto = 'L' if poi['POI_ST_SD'] == 'R' else 'R'
poi_opuesto = ubicar_poi(link_geom, poi['PERCFRREF'], lado_opuesto)


# Visualización
x_line, y_line = link_geom.xy
plt.plot(x_line, y_line, color='black', linewidth=2, label='Calle')
plt.scatter(poi_geom.x, poi_geom.y, color='green', label=f'POI {poi["POI_ST_SD"]}')
plt.scatter(poi_opuesto.x, poi_opuesto.y, color='red', label=f'POI {lado_opuesto}')
plt.legend()
plt.title(f"POI real vs lado opuesto (ID: {poi['POI_ID']})")
plt.axis('equal')
plt.grid(True)
plt.show()
