"""Flatten a picture to the palette before it is traced."""
import numpy as np
from PIL import Image, ImageFilter
from skimage import color
from scipy import ndimage as ndi
PAINT = "#d9a93f #ecd9a0 #7c8b3f #c98b7a #c9b48f #8a6a45 #2f4f77 #f1ead8 #a37d33 #e2d5b7".split()
pairs = {h: h for h in PAINT}; pairs.update({"#e9dab9": "#e2d5b7", "#f8cc68": "#ecd9a0", "#f5c357": "#ecd9a0"})
def rgb(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]
im = Image.open("src2.png").convert("RGB").filter(ImageFilter.MedianFilter(3))
lab = color.rgb2lab(np.asarray(im, dtype=float) / 255)
keys = list(pairs); kl = color.rgb2lab(np.array([rgb(k) for k in keys], dtype=float).reshape(1, -1, 3) / 255)[0]
lbl = np.stack([((lab - k) ** 2).sum(-1) for k in kl]).argmin(0)
to = np.array([PAINT.index(pairs[k]) for k in keys])[lbl]
to = ndi.median_filter(to, 5)
Image.fromarray(np.array([rgb(h) for h in PAINT], dtype=np.uint8)[to]).save("src2-flat.png")
