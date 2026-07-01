"""Generate Capacitor source assets: resources/icon.png (1024) + resources/splash.png (2732)."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os

ROOT = os.path.dirname(__file__)
OUT = os.path.join(ROOT, "assets")
os.makedirs(OUT, exist_ok=True)

def radial_bg(size, c_in, c_out):
    img = Image.new("RGB", (size, size), c_out)
    px = img.load()
    cx = cy = size / 2
    maxd = math.hypot(cx, cy)
    for y in range(size):
        for x in range(size):
            d = min(1.0, math.hypot(x - cx, y - cy) / maxd)
            px[x, y] = tuple(int(c_in[i] + (c_out[i] - c_in[i]) * d) for i in range(3))
    return img

def bolt(size, cx, cy, scale):
    """return polygon points for a lightning bolt centered at cx,cy sized by scale (px)."""
    def P(fx, fy):
        return (cx + (fx - 0.5) * scale, cy + (fy - 0.5) * scale)
    return [P(0.60,0.05),P(0.30,0.52),P(0.48,0.52),P(0.38,0.95),P(0.74,0.42),P(0.54,0.42)]

def draw_bolt(img, cx, cy, scale, ss_blur):
    S = img.size[0]
    pts = bolt(S, cx, cy, scale)
    # magenta + cyan glow
    for col, blur in [((255,47,179,255), ss_blur*1.8), ((34,230,255,255), ss_blur)]:
        g = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(g).polygon(pts, fill=col)
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))
    # gradient bolt (cyan->magenta)
    grad = Image.new("RGBA", img.size, (0,0,0,0))
    gpx = grad.load()
    top=(150,245,255); bot=(255,120,210)
    y0 = int(cy - scale/2); y1 = int(cy + scale/2)
    for y in range(img.size[1]):
        t = min(1.0, max(0.0, (y - y0) / max(1,(y1 - y0))))
        c = tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3)) + (255,)
        for x in range(img.size[0]):
            gpx[x,y] = c
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    img.paste(grad, (0,0), mask)

# ---- ICON 1024 (with safe padding for adaptive cropping) ----
S = 1024
icon = radial_bg(S, (18,26,48), (5,6,10)).convert("RGBA")
draw_bolt(icon, S/2, S/2, S*0.52, S*0.05)
icon.convert("RGB").save(os.path.join(OUT, "icon.png"))

# ---- SPLASH 2732 (dark bg, centered bolt + wordmark) ----
SP = 2732
sp = radial_bg(SP, (14,20,40), (5,6,10)).convert("RGBA")
draw_bolt(sp, SP/2, SP/2 - 120, SP*0.22, SP*0.02)
# wordmark
try:
    font = None
    for cand in ["C:/Windows/Fonts/arialbd.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            font = ImageFont.truetype(cand, 200); break
        except Exception:
            continue
    if font:
        d = ImageDraw.Draw(sp)
        txt = "VOLT"
        bb = d.textbbox((0,0), txt, font=font)
        w = bb[2]-bb[0]; h = bb[3]-bb[1]
        d.text(((SP-w)/2 - bb[0], SP/2 + 380), txt, font=font, fill=(190,246,255,255))
except Exception as e:
    print("wordmark skipped:", e)
sp.convert("RGB").save(os.path.join(OUT, "splash.png"))
# dark variant identical (already dark)
sp.convert("RGB").save(os.path.join(OUT, "splash-dark.png"))

print("resources written:", os.listdir(OUT))
