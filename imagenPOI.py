from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
from skimage.filters import threshold_otsu

# === 1. Cargar imagen y convertir a RGB (descarta canal alfa si existe) ===
imagen = Image.open("/Users/ebonyvaladez/Desktop/data/docs/satellite_tile.png")
img_rgb = imagen.convert("RGB")            # Asegura que tiene solo 3 canales (RGB)
img_np = np.array(img_rgb)                 # Convertir a arreglo numpy

# === 2. Convertir a escala de grises ===
gray = rgb2gray(img_np)                    # Convierte RGB a escala de grises (valores entre 0 y 1)

# === 3. Binarizar usando threshold de Otsu ===
thresh = threshold_otsu(gray)
binary = gray < thresh                     # True = oscuro, False = claro

# === 4. Visualizar resultados ===
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

axs[0].imshow(img_rgb)
axs[0].set_title("Imagen RGB")
axs[0].axis("off")

axs[1].imshow(gray, cmap="gray")
axs[1].set_title("Escala de grises")
axs[1].axis("off")

axs[2].imshow(binary, cmap="gray")
axs[2].set_title("Binarizada (Otsu)")
axs[2].axis("off")

plt.tight_layout()
plt.show()