import json
import pandas as pd

def obtener_puntos_inicio_fin_por_link(geojson_path):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    puntos_por_link = {}

    for feature in data.get('features', []):
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})
        tipo = geometry.get('type', '')
        coords = geometry.get('coordinates', [])
        link_id = properties.get('link_id')

        if link_id is None or tipo != 'LineString' or len(coords) < 2:
            continue

        link_id = str(link_id).upper()
        inicio = coords[0][:2]
        fin = coords[-1][:2]
        puntos_por_link[link_id] = {'inicio': inicio, 'fin': fin}

    return puntos_por_link

def interpolar_punto(inicio, fin, porcentaje):
    lon1, lat1 = inicio
    lon2, lat2 = fin
    lat = lat1 + (lat2 - lat1) * porcentaje
    lon = lon1 + (lon2 - lon1) * porcentaje
    return (lat, lon)

def calcular_pois_desde_porcentaje(pois_csv, lineas_geojson, salida_csv='pois_interpolados.csv'):
    puntos_por_linea = obtener_puntos_inicio_fin_por_link(lineas_geojson)
    df_pois = pd.read_csv(pois_csv)

    resultados = []

    for _, row in df_pois.iterrows():
        link_id = str(row['link_id']).upper()
        porcentaje = row['PERCFRREF']
        poi_id = row.get('POI_ID', None)  # Puedes ajustar el nombre si tienes un identificador

        puntos = puntos_por_linea.get(link_id)
        if puntos:
            lat, lon = interpolar_punto(puntos['inicio'], puntos['fin'], porcentaje)
            print(f"POI en LINK_ID {link_id} ({porcentaje*100:.1f}%): lat = {lat:.6f}, lon = {lon:.6f}")
            resultados.append({
                'id': poi_id,
                'link_id': link_id,
                'porcentaje': porcentaje,
                'lat': lat,
                'lon': lon
            })
        else:
            print(f"⚠ No se encontró geometría para LINK_ID {link_id}")
            resultados.append({
                'id': poi_id,
                'link_id': link_id,
                'porcentaje': porcentaje,
                'lat': None,
                'lon': None
            })

    # Guardar resultados en CSV
    df_resultado = pd.DataFrame(resultados)
    df_resultado.to_csv(salida_csv, index=False)
    print(f"\n✔ Resultados guardados en '{salida_csv}'")

calcular_pois_desde_porcentaje(
    pois_csv='/Users/ebonyvaladez/Desktop/data/POIs/POI_4815075.csv',
    lineas_geojson='/Users/ebonyvaladez/Desktop/data/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815075.geojson',
    salida_csv='/Users/ebonyvaladez/Desktop/data/pois_interpolados.csv'
)

