import json
import pandas as pd
from shapely.geometry import shape, LineString
from shapely.ops import transform
import pyproj

def ordenar_coords_por_criterio(coords):
    """
    Ordena las coordenadas según latitud, luego longitud, luego z-level (si hay).
    """
    return sorted(coords, key=lambda c: (c[1], c[0], c[2] if len(c) > 2 else 0))

def reordenar_linestring_si_es_necesario(linea):
    coords = list(linea.coords)
    ordenadas = ordenar_coords_por_criterio(coords)
    inicio_deseado = ordenadas[0]
    
    if coords[0] != inicio_deseado:
        coords.reverse()
    return LineString(coords)

def proyectar_a_metrico(geom):
    project = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
    return transform(project, geom)

def reproyectar_a_wgs84(geom):
    project = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform
    return transform(project, geom)

def interpolar_punto_en_linea(linea, porcentaje):
    linea_ordenada = reordenar_linestring_si_es_necesario(linea)
    linea_m = proyectar_a_metrico(linea_ordenada)
    distancia = linea_m.length * porcentaje
    punto_m = linea_m.interpolate(distancia)
    punto = reproyectar_a_wgs84(punto_m)
    return punto.y, punto.x  # lat, lon

def cargar_lineas_como_diccionario(geojson_path):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    lineas_por_link = {}

    for feature in data.get('features', []):
        link_id = feature['properties'].get('link_id')
        if link_id is None:
            continue
        link_id = str(link_id).upper()

        geom = feature.get('geometry')
        if geom and geom['type'] == 'LineString':
            linea = shape(geom)
            lineas_por_link[link_id] = linea

    return lineas_por_link

def calcular_pois_desde_porcentaje(pois_csv, lineas_geojson, salida_csv='pois_interpolados.csv'):
    lineas_por_link = cargar_lineas_como_diccionario(lineas_geojson)
    df_pois = pd.read_csv(pois_csv)

    resultados = []

    for _, row in df_pois.iterrows():
        link_id = str(row['LINK_ID']).upper()
        porcentaje = row['PERCFRREF']
        poi_id = row.get('POI_ID', None)

        linea = lineas_por_link.get(link_id)
        if linea:
            lat, lon = interpolar_punto_en_linea(linea, porcentaje)
            print(f"POI {poi_id} en LINK_ID {link_id} ({porcentaje:.1f}%): lat = {lat:.6f}, lon = {lon:.6f}")
            resultados.append({
                'id': poi_id,
                'link_id': link_id,
                'porcentaje': porcentaje,
                'lat': lat,
                'lon': lon
            })
        else:
            print(f"⚠ No se encontró línea para LINK_ID {link_id}")
            resultados.append({
                'id': poi_id,
                'link_id': link_id,
                'porcentaje': porcentaje,
                'lat': None,
                'lon': None
            })

    df_resultado = pd.DataFrame(resultados)
    df_resultado.to_csv(salida_csv, index=False)
    print(f"\n✔ Resultados correctos guardados en '{salida_csv}'")

calcular_pois_desde_porcentaje(
    pois_csv='/Users/ebonyvaladez/Desktop/data/POIs/POI_4815075.csv',
    lineas_geojson='/Users/ebonyvaladez/Desktop/data/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815075.geojson',
    salida_csv='/Users/ebonyvaladez/Desktop/data/pois_interpolados.csv'
)

