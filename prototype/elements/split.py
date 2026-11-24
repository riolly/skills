"""Cut the element sheet into one PNG per element, with the background replaced by a key colour."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
KEY = (0, 255, 255)
im = Image.open("sheet.png").convert("RGB"); a = np.asarray(im).astype(int)
ground = np.median(a[:40, :40].reshape(-1, 3), axis=0)
near = np.abs(a - ground).sum(-1) < 26
lab, n = ndi.label(near)
border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
bg = np.isin(lab, border[border > 0])
bg = ndi.binary_dilation(bg, iterations=2)
out = a.copy(); out[bg] = KEY
objs, n = ndi.label(ndi.binary_dilation(~bg, iterations=22))
names = [["gleaner", "reaper_green", "reaper_brown", "winnower"], ["clinging", "family", "elders", "moon"], ["barley", "sheaf", "gate", "ear"]]
H, W = bg.shape
for i, sl in enumerate(ndi.find_objects(objs), 1):
    part = (objs[sl] == i) & ~bg[sl]
    if part.sum() < 3000: continue
    ys, xs = np.where(part); cy, cx = sl[0].start + ys.mean(), sl[1].start + xs.mean()
    name = names[int(cy * 3 // H)][int(cx * 4 // W)]
    if name == "moon" and cy > H * 0.5: name = "heap"
    y0, y1, x0, x1 = sl[0].start + ys.min() - 8, sl[0].start + ys.max() + 8, sl[1].start + xs.min() - 8, sl[1].start + xs.max() + 8
    crop = out[y0:y1, x0:x1].copy()
    crop[(objs[y0:y1, x0:x1] != i)] = KEY
    c = Image.fromarray(crop.astype(np.uint8))
    c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
    c.save(f"el2/{name}.png"); print(name, c.size)
