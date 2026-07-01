"""Generate VOLT app icons (neon lightning bolt) with Pillow."""
from PIL import Image, ImageDraw, ImageFilter
import math, os

OUT = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(OUT, exist_ok=True)

def radial_bg(size, c_in, c_out):
    img = Image.new("RGB", (size, size), c_out)
    px = img.load()
    cx = cy = size / 2
    maxd = math.hypot(cx, cy)
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy) / maxd
            d = min(1.0, d)
            px[x, y] = tuple(int(c_in[i] + (c_out[i] - c_in[i]) * d) for i in range(3))
    return img

def bolt_points(size, pad):
    # a lightning bolt polygon within [pad, size-pad]
    w = size - 2 * pad
    def P(fx, fy):
        return (pad + fx * w, pad + fy * w)
    return [
        P(0.60, 0.05), P(0.30, 0.52), P(0.48, 0.52),
        P(0.38, 0.95), P(0.74, 0.42), P(0.54, 0.42),
    ]

def make(size, maskable=False):
    ss = 4  # supersample
    S = size * ss
    pad = int(S * (0.20 if maskable else 0.12))
    bg = radial_bg(S, (18, 26, 48), (5, 6, 10)).convert("RGBA")

    # glow layer (magenta + cyan)
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    pts = bolt_points(S, pad)
    gd.polygon(pts, fill=(34, 230, 255, 255))
    glow_c = glow.filter(ImageFilter.GaussianBlur(S * 0.06))

    glow2 = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(glow2)
    gd2.polygon(pts, fill=(255, 47, 179, 255))
    glow_m = glow2.filter(ImageFilter.GaussianBlur(S * 0.11))

    bg = Image.alpha_composite(bg, glow_m)
    bg = Image.alpha_composite(bg, glow_c)

    # crisp bolt with vertical cyan -> magenta gradient
    grad = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gpx = grad.load()
    top = (150, 245, 255); bot = (255, 120, 210)
    for y in range(S):
        t = y / S
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,)
        for x in range(S):
            gpx[x, y] = col
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    bg.paste(grad, (0, 0), mask)

    # inner white highlight
    hi = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    inner = [((p[0] - S/2) * 0.55 + S/2, (p[1] - S/2) * 0.55 + S/2) for p in pts]
    hd.polygon(inner, fill=(255, 255, 255, 210))
    hi = hi.filter(ImageFilter.GaussianBlur(S * 0.006))
    bg = Image.alpha_composite(bg, hi)

    out = bg.resize((size, size), Image.LANCZOS).convert("RGB")
    return out

make(192).save(os.path.join(OUT, "icon-192.png"))
make(512).save(os.path.join(OUT, "icon-512.png"))
make(512, maskable=True).save(os.path.join(OUT, "icon-maskable-512.png"))
# a big one for social/apple
make(180).save(os.path.join(OUT, "apple-touch-180.png"))
print("icons written to", OUT)
