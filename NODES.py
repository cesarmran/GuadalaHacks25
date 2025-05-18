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
        link_id = str(properties.get('link_id'))

        if tipo == 'LineString' and len(coords) >= 2:
            inicio = coords[0][:2]  # [lon, lat]
            fin = coords[-1][:2]
            puntos_por_link[link_id] = {'inicio': inicio, 'fin': fin}

    return puntos_por_link

def interpolar_punto(inicio, fin, porcentaje):
    lon1, lat1 = inicio
    lon2, lat2 = fin
    lat = lat1 + (lat2 - lat1) * porcentaje
    lon = lon1 + (lon2 - lon1) * porcentaje
    return (lat, lon)

def calcular_pois_desde_porcentaje(pois_csv, lineas_geojson):
    puntos_por_linea = obtener_puntos_inicio_fin_por_link(lineas_geojson)
    df_pois = pd.read_csv(pois_csv)

    for _, row in df_pois.iterrows():
        link_id = str(row['LIMK_ID'])
        porcentaje = row['PERCFRREF']

        puntos = puntos_por_linea.get(link_id)
        if puntos:
            lat, lon = interpolar_punto(puntos['inicio'], puntos['fin'], porcentaje)
            print(f"POI en link_id {link_id} ({porcentaje*100:.1f}%): lat = {lat:.6f}, lon = {lon:.6f}")
        else:
            print(f"⚠ No se encontró geometría para link_id {link_id}")


calcular_pois_desde_porcentaje('/Users/ebonyvaladez/Desktop/data/POIs/POI_4815075.csv', '/Users/ebonyvaladez/Desktop/data/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815075.geojson')

