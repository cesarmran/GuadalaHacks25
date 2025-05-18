import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point
import numpy as np
from PIL import Image

def lado_del_poi(linea, poi_point, porcentaje):
    """
    Determina si el POI está a la izquierda, derecha o sobre la línea
    según el sentido de la línea del punto interpolado.
    
    Parámetros:
    - linea: objeto shapely LineString
    - poi_point: objeto shapely Point (lat/lon del POI)
    - porcentaje: posición del POI en la línea (entre 0 y 1)

    Retorna:
    - 'izquierda', 'derecha' o 'sobre la línea'
    """
    # Punto en la línea según el porcentaje (punto base)
    p1 = linea.interpolate(linea.length * porcentaje)
    
    # Punto un poco más adelante en la línea para formar un vector direccional
    delta = 0.01  # pequeño paso hacia adelante (1%)
    p2 = linea.interpolate(min(linea.length * (porcentaje + delta), linea.length))

    # Vector de dirección de la línea (p1 → p2)
    v = np.array([p2.x - p1.x, p2.y - p1.y])
    
    # Vector desde la línea hacia el POI (p1 → poi)
    w = np.array([poi_point.x - p1.x, poi_point.y - p1.y])

    # Producto cruzado (determinante en 2D)
    det = v[0] * w[1] - v[1] * w[0]

    if det > 0:
        return "izquierda"
    elif det < 0:
        return "derecha"
    else:
        return "sobre la línea"

# Línea de ejemplo: calle de oeste a este
linea = LineString([(-99.62957, 19.27045), (-99.6297 ,19.27056)])
poi = Point(-99.629635, 19.270505)
porcentaje = .50

# Verificar de qué lado está
lado = lado_del_poi(linea, poi, porcentaje)
print(f"El POI está a la {lado} de la línea.")

# === Punto de interpolación y dirección ===
p1 = linea.interpolate(linea.length * porcentaje)
p2 = linea.interpolate(min(linea.length * (porcentaje + 0.01), linea.length))

# === Preparar coordenadas ===
x_line, y_line = linea.xy
x_vector = [p1.x, p2.x]
y_vector = [p1.y, p2.y]

# === Bbox del tile ===
xmin = -99.635009765625
xmax = -99.6240234375
ymin = 19.269665296502325
ymax = 19.28003579627975

from PIL import Image

tile = Image.open("/Users/ebonyvaladez/Desktop/data/docs/satellite_tile.png")  
# Gráfico
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(tile, extent=[xmin, xmax, ymin, ymax], origin='upper')  # fondo tile

# Geometrías
ax.plot(x_line, y_line, color='blue', linewidth=2, label='Línea (sentido →)')
ax.arrow(p1.x, p1.y, p2.x - p1.x, p2.y - p1.y, head_width=0.0001, color='black', length_includes_head=True, label='Dirección')
ax.plot(p1.x, p1.y, 'go', label='Punto interpolado')
ax.plot(poi.x, poi.y, 'ro', markersize=10, label='POI')

# Estilo
ax.set_title(f'POI está a la {lado} de la línea')
ax.set_xlabel('Longitud')
ax.set_ylabel('Latitud')
ax.axis('equal')
ax.grid(True)
ax.legend()
plt.tight_layout()
plt.show()

