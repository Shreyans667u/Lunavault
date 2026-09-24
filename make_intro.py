import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
FPS = 30
DURATION = 5.6
NFRAMES = int(FPS * DURATION)
OUT_DIR = "/home/claude/frames"
os.makedirs(OUT_DIR, exist_ok=True)

VOID = (10, 13, 26)
LUNAR = (199, 203, 224)
DUST_DIM = (125, 132, 168)
GLOW = (154, 163, 240)
GOLD = (227, 193, 126)

random.seed(7)
NUM_DUST = 160
dust = [{
    "x": random.uniform(0, W),
    "y": random.uniform(0, H),
    "r": random.uniform(0.6, 2.0),
    "base_a": random.uniform(0.18, 0.6),
    "phase": random.uniform(0, 2 * math.pi),
    "speed": random.uniform(0.6, 1.4),
    "drift": random.uniform(-6, 6),
} for _ in range(NUM_DUST)]

def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + (b - a) * t

word_font = ImageFont.truetype("/home/claude/fraunces_italic.ttf", 108)
word_font.set_variation_by_axes([48, 460, 0, 1])  # opsz, weight, softness, wonky
tag_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)

WORD1 = "Luna"
WORD2 = "vault"
TAGLINE = "Your saved posts, sorted out of the pile."

# precompute glow layer once (soft radial), tinted, reused with varying alpha/scale
def make_glow(radius, color, size=900):
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = size // 2, size // 2
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.35))
    return layer

glow_layer = make_glow(220, GLOW)

def render_frame(i):
    t = i / FPS  # seconds
    img = Image.new("RGB", (W, H), VOID)

    # --- dust field (fades in over first 0.8s, gentle twinkle throughout) ---
    dust_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust_layer)
    field_in = ease_out_cubic(t / 0.9)
    for p in dust:
        twinkle = 0.5 + 0.5 * math.sin(p["phase"] + t * p["speed"])
        a = p["base_a"] * field_in * (0.5 + 0.5 * twinkle)
        x = p["x"] + p["drift"] * (t / DURATION)
        dd.ellipse([x - p["r"], p["y"] - p["r"], x + p["r"], p["y"] + p["r"]],
                   fill=LUNAR + (int(a * 255),))
    img.paste(dust_layer, (0, 0), dust_layer)

    # --- moon glow, top-right, gentle pulse + fade in ---
    glow_in = ease_out_cubic((t - 0.15) / 1.1)
    pulse = 1.0 + 0.05 * math.sin(t * 1.3)
    if glow_in > 0:
        scale = (0.85 + 0.15 * glow_in) * pulse
        gsize = int(900 * scale)
        g = glow_layer.resize((gsize, gsize), Image.LANCZOS)
        alpha = g.split()[3].point(lambda a: int(a * 0.55 * glow_in))
        g.putalpha(alpha)
        img.paste(g, (W - gsize + 260, -gsize + 340), g)

    draw = ImageDraw.Draw(img)

    # --- wordmark: fade + rise, staggered "Luna" then "vault" ---
    w1_t = ease_out_cubic((t - 0.9) / 0.9)
    w2_t = ease_out_cubic((t - 1.15) / 0.9)
    rise = lambda p: int(lerp(18, 0, p))

    bbox1 = draw.textbbox((0, 0), WORD1, font=word_font)
    bbox2 = draw.textbbox((0, 0), WORD2, font=word_font)
    w1_w = bbox1[2] - bbox1[0]
    w2_w = bbox2[2] - bbox2[0]
    total_w = w1_w + w2_w
    start_x = (W - total_w) // 2
    base_y = H // 2 - 40

    if w1_t > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text((start_x, base_y + rise(w1_t)), WORD1, font=word_font,
                 fill=LUNAR + (int(255 * w1_t),))
        img.paste(layer, (0, 0), layer)
    if w2_t > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text((start_x + w1_w, base_y + rise(w2_t)), WORD2, font=word_font,
                 fill=GOLD + (int(255 * w2_t),))
        img.paste(layer, (0, 0), layer)

    # --- tagline ---
    tag_t = ease_out_cubic((t - 2.0) / 0.9)
    if tag_t > 0:
        tb = draw.textbbox((0, 0), TAGLINE, font=tag_font)
        tw = tb[2] - tb[0]
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text(((W - tw) // 2, base_y + 118 + rise(tag_t) * 0.6), TAGLINE,
                 font=tag_font, fill=DUST_DIM + (int(230 * tag_t),))
        img.paste(layer, (0, 0), layer)

    # --- hairline accent under wordmark, drawn in on a delay ---
    line_t = ease_in_out((t - 1.6) / 0.7)
    if line_t > 0:
        lw = int(120 * line_t)
        cx = W // 2
        y = base_y + 95
        draw.line([(cx - lw, y), (cx + lw, y)], fill=(*GOLD, ), width=1)

    # --- fade to void at the very end ---
    fade_out = ease_in_out((t - (DURATION - 0.7)) / 0.7)
    if fade_out > 0:
        overlay = Image.new("RGB", (W, H), VOID)
        img = Image.blend(img, overlay, min(1.0, fade_out))

    return img

for i in range(NFRAMES):
    frame = render_frame(i)
    frame.save(f"{OUT_DIR}/f{i:04d}.png")

print("done", NFRAMES, "frames")
