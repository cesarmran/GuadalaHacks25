import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import math

# Función que calcula la posición del POI a lo largo de la calle y hacia un lado
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

# Función que detecta errores en cada POI
def detectar_error_poi(poi, calles):
    resultado = {
        "POI_ID": poi["POI_ID"],
        "LINK_ID": poi["LINK_ID"],
        "POI_ST_SD": poi["POI_ST_SD"],
        "Error": "",
        "Accion": ""
    }

    if poi["LINK_ID"] not in calles["link_id"].values:
        resultado["Error"] = "No se encontró LINK_ID"
        resultado["Accion"] = "Revisar vínculo con calle"
        return resultado

    geom_calle = calles[calles["link_id"] == poi["LINK_ID"]].geometry.values[0]
    perc = poi["PERCFRREF"]
    lado = poi["POI_ST_SD"]
    geom_poi = ubicar_poi(geom_calle, perc, lado)
    distancia = geom_poi.distance(geom_calle)

    if distancia > 0.0008:
        resultado["Error"] = "POI alejado de la calle"
        resultado["Accion"] = "Eliminar POI"
    else:
        geom_opuesto = ubicar_poi(geom_calle, perc, "L" if lado == "R" else "R")
        dist_lado = geom_poi.distance(ubicar_poi(geom_calle, perc, lado))
        dist_opuesto = geom_poi.distance(geom_opuesto)

        if dist_opuesto < dist_lado:
            resultado["Error"] = "POI en lado incorrecto"
            resultado["Accion"] = f'Cambiar POI_ST_SD a {"L" if lado == "R" else "R"}'
        else:
            resultado["Error"] = "Correcto o excepción válida"
            resultado["Accion"] = "Validar"

    return resultado

# Rutas a tus archivos (ajusta a tu computadora)
ruta_pois = "C:/Users/cmora/Downloads/DATA/POIs/POI_4815098.csv"
ruta_calles = "C:/Users/cmora/Downloads/DATA/STREETS_NAV/SREETS_NAV_4815096.geojson"
salida_csv = "C:/Users/cmora/Documents/excelErroresGH/poIs_resultado.csv"

# Cargar datos
calles = gpd.read_file(ruta_calles)
pois = pd.read_csv(ruta_pois)

# Filtrar solo POIs con calle válida
pois_validos = pois[pois["LINK_ID"].isin(calles["link_id"])]

# Analizar todos los POIs
resultados = []
for _, poi in pois_validos.iterrows():
    resultados.append(detectar_error_poi(poi, calles))

# Guardar en CSV
df_resultados = pd.DataFrame(resultados)
df_resultados.to_csv(salida_csv, index=False)
print(f"✅ Análisis completado. Resultados guardados en:\n{salida_csv}")
