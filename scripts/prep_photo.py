"""
Prepare a portrait photo for clean ASCII conversion:
  1. remove the background (rembg) so the subject is isolated
  2. boost LOCAL contrast (CLAHE) so a flatly-lit face gains highlights and
     shadows -- this is what turns a dark blob into a recognizable face
  3. composite the subject onto pure white so the background reads as blank
     (white -> spaces in the ascii ramp)
  4. crop a square around the head and shoulders -- make_ascii_svg.py samples
     a ~square character grid, so a 3:4 phone photo would squash, and a
     bigger face keeps the glasses and smile readable at ascii resolution

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
Run once whenever the source photo changes; the ascii SVG itself is static.

    pip install -r scripts/requirements-portrait.txt
    python scripts/prep_photo.py ["Youssef Ismail.jpeg"] [source-prepped.png]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageOps
from rembg import new_session, remove

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "Youssef Ismail.jpeg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

# u2net rather than rembg's newer default (bria-rmbg): it cuts the person off
# at the table edge instead of keeping the table, and it's a 176 MB download
# instead of 1 GB.
MODEL = "u2net"
CLAHE_CLIP = 3.5      # local contrast: higher = darker glasses/brows vs skin
LIFT = 8              # global brightness lift after CLAHE
SIDE = 0.67           # crop side as a fraction of the subject's width
HEADROOM = 0.075      # gap above the hair, as a fraction of the crop side

# 1. cut out the subject
photo = ImageOps.exif_transpose(Image.open(INP)).convert("RGBA")
cut = remove(photo, session=new_session(MODEL))
rgb = np.array(cut.convert("RGB"))
alpha = np.array(cut.split()[-1])                 # 0 = background

# 2. local-contrast the luminance (CLAHE)
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=(8, 8))
gray = clahe.apply(gray)

# a touch of global lift so the face sits in the sparse end of the ramp
gray = cv2.convertScaleAbs(gray, alpha=1.05, beta=LIFT)

# 3. paste onto white using the alpha mask (feathered a hair to avoid a halo)
mask = (alpha.astype(np.float32) / 255.0)
mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
out = gray.astype(np.float32) * mask + 255.0 * (1.0 - mask)
out = np.clip(out, 0, 255).astype(np.uint8)

# 4. square crop: centred on the head (the top band of the cutout), hair just
#    below the top edge; anything outside the photo stays white
ys, xs = np.where(alpha > 20)
side = int((xs.max() - xs.min()) * SIDE)
head_top = ys.min()
cx = int(np.nonzero(alpha[head_top:head_top + side // 3] > 20)[1].mean())
x0, y0 = cx - side // 2, head_top - int(side * HEADROOM)
canvas = np.full((side, side), 255, np.uint8)
sx0, sy0 = max(x0, 0), max(y0, 0)
sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out[sy0:sy1, sx0:sx1]

Image.fromarray(canvas, mode="L").save(OUT)
print("wrote", OUT, canvas.shape, "crop x", x0, "y", y0, "side", side)
