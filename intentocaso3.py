import geopandas as gpd

def cargar_links(path_archivo):
    gdf = gpd.read_file(path_archivo)
    print("Archivo cargado:", path_archivo)
    print("Columnas disponibles:", gdf.columns.tolist())
    return gdf

def analizar_multipdigit_y_sugerir(gdf_links, link_id_objetivo):
    segmento = gdf_links[gdf_links['link_id'] == link_id_objetivo]
    if segmento.empty:
        return None  # No existe

    segmento = segmento.iloc[0]

    # Regla: si alguno de estos está presente, MULTIDIGIT debe ser 'N'
    if segmento.get('RAMP') == 'Y' or segmento.get('DIR_TRAVEL') == 'B' or segmento.get('MANEUVER') == 'Y':
        return link_id_objetivo  # Sugerencia de corrección

    # Proyección para medir distancias
    gdf_proj = gdf_links.to_crs(epsg=3857)
    geom_segmento = gdf_proj[gdf_proj['link_id'] == link_id_objetivo].geometry.iloc[0]
    longitud = geom_segmento.length

    otros = gdf_proj[gdf_proj['link_id'] != link_id_objetivo].copy()
    otros['distancia'] = otros.geometry.distance(geom_segmento)
    cerca = otros[otros['distancia'] <= 80]

    # Evaluar si debe corregirse
    if segmento['MULTIDIGIT'] == 'Y' and cerca.empty:
        return link_id_objetivo  # marcado como Y pero no hay otro cerca → inválido

    return None  # No se sugiere corrección


def analizar_todos_los_links_y_guardar(gdf_links):
    ids_corregir = []

    for link_id in gdf_links['link_id'].unique():
        sugerencia = analizar_multipdigit_y_sugerir(gdf_links, link_id_objetivo=link_id)
        if sugerencia is not None:
            ids_corregir.append(sugerencia)

    print("\nAnálisis completado.")
    print(f"Total de links analizados: {len(gdf_links['link_id'].unique())}")
    print(f"Links que deberían corregirse: {len(ids_corregir)}")
    return ids_corregir



# 1. Cargar archivo
gdf = cargar_links("/Users/ebonyvaladez/Desktop/data/STREETS_NAV/SREETS_NAV_4815075.geojson")

# 2. Obtener lista de links con MULTIDIGIT incorrecto
links_con_error = analizar_todos_los_links_y_guardar(gdf)

# 3. Mostrar resultados
print("IDs con MULTIDIGIT incorrecto:")
print(links_con_error)



