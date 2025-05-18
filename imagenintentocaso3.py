import matplotlib.pyplot as plt
from PIL import Image
import geopandas as gpd
from shapely.geometry import Point, LineString

# --- 1. Función para convertir coordenadas geográficas a píxeles ---
def geo_to_pixel(lon, lat, bbox, image_size):
    min_lon, max_lon = bbox[0], bbox[2]
    min_lat, max_lat = bbox[3], bbox[1]

    x = (lon - min_lon) / (max_lon - min_lon) * image_size[0]
    y = (1 - (lat - min_lat) / (max_lat - min_lat)) * image_size[1]
    return int(x), int(y)

# --- 2. Mostrar imagen con overlay de POI y link ---
def mostrar_validacion_satelital(imagen_path, bbox, poi_coords, gdf_links, link_id_objetivo):
    # Abrir imagen satelital
    img = Image.open(imagen_path)
    img_size = img.size

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(img)

    # Marcar POI
    x, y = geo_to_pixel(poi_coords[0], poi_coords[1], bbox, img_size)
    ax.plot(x, y, 'ro', label='POI')

    # Dibujar el link objetivo
    link = gdf_links[gdf_links['link_id'] == link_id_objetivo]
    if not link.empty:
        line = link.iloc[0].geometry
        if line.geom_type == 'LineString':
            lonlats = list(line.coords)
        elif line.geom_type.startswith('Multi'):
            lonlats = list(line.geoms[0].coords)
        else:
            lonlats = []

        pixel_coords = [geo_to_pixel(lon, lat, bbox, img_size) for lon, lat in lonlats]
        x_vals, y_vals = zip(*pixel_coords)
        ax.plot(x_vals, y_vals, color='blue', linewidth=2, label=f'Link {link_id_objetivo}')
    else:
        print(f"link_id {link_id_objetivo} no encontrado.")

    ax.set_title("Validación visual del POI y calle asociada")
    ax.legend()
    plt.axis('off')
    plt.show()

# Ruta a la imagen que subiste
imagen_path = "/Users/ebonyvaladez/Desktop/data/docs/satellite_tile.png"

# Coordenadas del POI (lon, lat)
poi_coords = (-99.62957, 19.27045)  # ejemplo, cámbialo por el real

# Bounding box: (min_lon, max_lat, max_lon, min_lat)
bbox = (-99.635009765625, 19.28003579627975, -99.6240234375, 19.269665296502325)

# Leer tu archivo de calles
gdf_links = gpd.read_file("/Users/ebonyvaladez/Desktop/data/STREETS_NAV/SREETS_NAV_4815075.geojson")

# Mostrar validación sobre la imagen
mostrar_validacion_satelital(imagen_path, bbox, poi_coords, gdf_links, link_id_objetivo=1341339647)
