#!/usr/bin/env python3
"""news-image-20261127: sum up Friday 27 November 2026 world news in one image.

Pure standard library, no network. Draws a 1024x1024 editorial poster with
six panels (one per story) and writes it to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png). Fully deterministic: two runs produce
identical bytes.

Stories (all reported 26-27 November 2026):
  1. EU summit stalls - no deal on the 45bn euro Ukraine loan (Brussels)
  2. Thanksgiving storm lashes the US East Coast; Black Friday opens
  3. Gaza strikes kill 10; Iranian drones kill two Italians in Kuwait
  4. Cairo fuel-tanker fire kills 31
  5. Vietnam races for a US trade deal before 35% tariffs
  6. London Tube drivers begin eight days of strikes
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
CREAM = (246, 241, 231)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
NAVY2 = (31, 78, 121)
GOLD = (212, 160, 23)
RED = (178, 34, 34)
SLATE = (44, 62, 80)
TEAL = (27, 122, 110)
BROWN = (122, 82, 40)
WHITE = (255, 255, 255)
GREY = (90, 90, 90)
LIGHTGREY = (220, 220, 220)
SKY = (135, 206, 235)
ORANGE = (230, 126, 34)
YELLOW = (241, 196, 15)
DUSK = (243, 156, 18)
SAND = (232, 216, 168)
SEA = (46, 134, 120)

# ------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '#' = on.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap(text, max_chars):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        nxt = (cur + ' ' + w).strip()
        if len(nxt) <= max_chars:
            cur = nxt
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x0, y0, x1, y1, c):
        x0 = max(0, x0); y0 = max(0, y0)
        x1 = min(self.w, x1); y1 = min(self.h, y1)
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1):
                i = base + (x - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def circle(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, c)

    def ring(self, cx, cy, r_out, r_in, c):
        for y in range(cy - r_out, cy + r_out + 1):
            for x in range(cx - r_out, cx + r_out + 1):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if r_in * r_in <= d2 <= r_out * r_out:
                    self.set(x, y, c)

    def line(self, x0, y0, x1, y1, c, w=1):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            x = x0 + dx * i // steps
            y = y0 + dy * i // steps
            self.rect(x - w // 2, y - w // 2, x + w // 2 + 1, y + w // 2 + 1, c)

    def triangle(self, ax, ay, bx, by, cx, cy, c):
        # scanline fill
        pts = sorted([(ax, ay), (bx, by), (cx, cy)], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts
        def interp(y, xa, ya, xb, yb):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) // (yb - ya)
        for y in range(y0, y2 + 1):
            if y < y1:
                xa = interp(y, x0, y0, x1, y1)
                xb = interp(y, x0, y0, x2, y2)
            else:
                xa = interp(y, x1, y1, x2, y2)
                xb = interp(y, x0, y0, x2, y2)
            if xa > xb:
                xa, xb = xb, xa
            self.rect(xa, y, xb + 1, y + 1, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        self.rect(cx + col * scale, y + r * scale,
                                  cx + (col + 1) * scale, y + (r + 1) * scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, c):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def text_right(self, x, y, s, scale, c):
        self.text(x - text_width(s, scale), y, s, scale, c)


# ------------------------------------------------------------ illustrations
def draw_eu(cv, x0, y0, x1, y1):
    """EU flag: blue field, circle of 12 gold stars, '45 BN' loan figure."""
    cv.rect(x0, y0, x1, y1, NAVY2)
    import math
    cx, cy, r = x0 + 95, (y0 + y1) // 2, 44
    for k in range(12):
        a = -math.pi / 2 + k * math.pi / 6
        sx = int(cx + r * math.cos(a))
        sy = int(cy + r * math.sin(a))
        cv.circle(sx, sy, 4, GOLD)
    tx = x0 + 190
    cv.text(tx, y0 + 18, "45 BN", 5, WHITE)
    cv.text(tx, y0 + 62, "EURO LOAN", 3, GOLD)
    cv.text(tx, y0 + 88, "STALLED", 2, WHITE)


def draw_storm(cv, x0, y0, x1, y1):
    """Storm cloud, rain, lightning over a city; Black Friday tag."""
    cv.rect(x0, y0, x1, y1, SLATE)
    # skyline
    base = y1 - 8
    for i, (bx, bw, bh) in enumerate([(0, 46, 34), (52, 30, 52), (88, 40, 28),
                                      (134, 34, 46), (174, 44, 30)]):
        cv.rect(x0 + bx, base - bh, x0 + bx + bw, base, (28, 40, 54))
    # cloud
    ccx, ccy = x0 + 95, y0 + 34
    for ox, oy, r in [(-38, 6, 20), (-14, -6, 26), (14, -2, 24), (38, 8, 18)]:
        cv.circle(ccx + ox, ccy + oy, r, (200, 205, 210))
    cv.rect(ccx - 58, ccy - 2, ccx + 56, ccy + 22, (200, 205, 210))
    # rain
    for rx in range(x0 + 30, x0 + 180, 18):
        cv.line(rx, ccy + 26, rx - 8, ccy + 48, SKY, 2)
    # lightning bolt
    bx, by = x0 + 200, y0 + 16
    cv.triangle(bx, by, bx + 18, by, bx + 6, by + 26, YELLOW)
    cv.triangle(bx + 6, by + 26, bx + 22, by + 26, bx - 2, by + 54, YELLOW)
    # wind streaks
    for wy in (y0 + 22, y0 + 40, y0 + 58):
        cv.line(x0 + 250, wy, x0 + 330, wy, WHITE, 2)
        cv.line(x0 + 262, wy + 6, x0 + 320, wy + 6, LIGHTGREY, 2)
    # price tag
    tx, ty = x0 + 330, y0 + 62
    cv.triangle(tx, ty, tx + 96, ty, tx + 96, ty + 34, RED)
    cv.rect(tx, ty, tx + 96, ty + 34, RED)
    cv.circle(tx + 12, ty + 17, 4, WHITE)
    cv.text(tx + 24, ty + 7, "SALE", 3, WHITE)


def draw_gaza(cv, x0, y0, x1, y1):
    """Dusk sky, skyline silhouettes, smoke column, setting sun."""
    cv.rect(x0, y0, x1, y1, DUSK)
    cv.rect(x0, y0 + 70, x1, y1, (120, 72, 20))
    # sun
    cv.circle(x0 + 400, y0 + 30, 20, (253, 231, 180))
    # skyline
    base = y1 - 6
    for bx, bw, bh in [(0, 52, 44), (58, 36, 66), (100, 48, 38),
                       (154, 30, 58), (190, 56, 42), (252, 40, 60),
                       (298, 46, 36), (350, 52, 50), (408, 48, 40)]:
        cv.rect(x0 + bx, base - bh, x0 + bx + bw, base, (58, 38, 24))
    # lit windows
    for wx in range(x0 + 8, x0 + 440, 26):
        cv.rect(wx, base - 30, wx + 5, base - 24, YELLOW)
    # smoke column
    sx = x0 + 120
    for oy, r in [(0, 9), (-14, 12), (-28, 15), (-42, 18)]:
        cv.circle(sx, y0 + 62 + oy, r, (96, 96, 96))
    cv.circle(sx - 8, y0 + 20, 14, (120, 120, 120))


def draw_cairo(cv, x0, y0, x1, y1):
    """Desert road, overturned tanker, flame, memorial candles."""
    cv.rect(x0, y0, x1, y1, SAND)
    # sun
    cv.circle(x0 + 410, y0 + 26, 18, (250, 200, 90))
    # road
    cv.rect(x0, y0 + 66, x1, y1 - 6, (74, 74, 74))
    cv.line(x0, y0 + 88, x1, y0 + 88, WHITE, 2)
    # overturned tanker: body on its side
    cv.rect(x0 + 40, y0 + 40, x0 + 210, y0 + 72, (180, 180, 180))
    cv.rect(x0 + 210, y0 + 46, x0 + 252, y0 + 72, (140, 140, 140))
    cv.circle(x0 + 70, y0 + 74, 9, INK)
    cv.circle(x0 + 110, y0 + 74, 9, INK)
    cv.circle(x0 + 190, y0 + 74, 9, INK)
    cv.circle(x0 + 228, y0 + 74, 9, INK)
    # flame above the tanker
    fx = x0 + 120
    cv.triangle(fx - 26, y0 + 42, fx, y0 + 2, fx + 26, y0 + 42, ORANGE)
    cv.triangle(fx - 13, y0 + 42, fx, y0 + 16, fx + 13, y0 + 42, YELLOW)
    # smoke
    for ox, oy, r in [(0, 0, 8), (10, -10, 11), (-8, -18, 13)]:
        cv.circle(x0 + 300, y0 + 30 + oy, r, (110, 110, 110))
    # memorial candles + toll
    for i in range(3):
        cx = x0 + 330 + i * 26
        cv.rect(cx, y0 + 78, cx + 8, y1 - 12, WHITE)
        cv.circle(cx + 4, y0 + 72, 4, YELLOW)
    cv.text(x0 + 330, y0 + 8, "31", 4, RED)


def draw_vietnam(cv, x0, y0, x1, y1):
    """Container ship on teal sea; big 35% tariff badge."""
    cv.rect(x0, y0, x1, y1, SEA)
    # waves
    for wy in (y0 + 78, y0 + 92):
        for wx in range(x0 + 10, x1 - 20, 34):
            cv.line(wx, wy, wx + 16, wy, WHITE, 2)
    # hull
    cv.triangle(x0 + 30, y0 + 62, x0 + 250, y0 + 62, x0 + 230, y0 + 86, (40, 40, 40))
    cv.rect(x0 + 30, y0 + 62, x0 + 250, y0 + 86, (40, 40, 40))
    # containers
    cols = [RED, GOLD, (40, 90, 160), (220, 120, 40)]
    for i, c in enumerate(cols):
        cv.rect(x0 + 46 + i * 48, y0 + 30, x0 + 88 + i * 48, y0 + 60, c)
    cv.rect(x0 + 46, y0 + 8, x0 + 140, y0 + 28, (200, 200, 200))
    # tariff badge
    bx, by = x0 + 330, y0 + 52
    cv.circle(bx, by, 44, WHITE)
    cv.ring(bx, by, 44, 38, RED)
    cv.text_center(bx, by - 22, "35%", 4, RED)
    cv.text_center(bx, by + 12, "TARIFF", 2, INK)


def draw_tube(cv, x0, y0, x1, y1):
    """London Underground roundel + picket sign."""
    cv.rect(x0, y0, x1, y1, WHITE)
    # roundel
    cx, cy = x0 + 110, y0 + 56
    cv.ring(cx, cy, 42, 30, RED)
    cv.rect(cx - 62, cy - 9, cx + 62, cy + 9, (0, 62, 140))
    cv.text_center(cx, cy - 7, "TUBE", 2, WHITE)
    # picket sign
    sx = x0 + 260
    cv.line(sx + 10, y0 + 30, sx + 10, y1 - 8, BROWN, 4)
    cv.rect(sx - 30, y0 + 6, sx + 110, y0 + 58, WHITE)
    cv.rect(sx - 30, y0 + 6, sx + 110, y0 + 58, INK)  # border via outline trick
    cv.rect(sx - 28, y0 + 8, sx + 108, y0 + 56, WHITE)
    cv.text(sx - 18, y0 + 15, "STRIKE", 3, RED)
    cv.text(sx - 18, y0 + 39, "8 DAYS", 2, INK)
    # crowd dots
    for i in range(6):
        cv.circle(x0 + 300 + i * 22, y1 - 14, 6, SLATE)


# ---------------------------------------------------------------- panels
PANELS = [
    dict(kicker="EUROPE - BRUSSELS", accent=NAVY2,
         headline="EU SUMMIT STALLS ON 45BN EURO UKRAINE LOAN",
         caption="Brussels summit ends with no deal on the budget or Kyiv's 2027 funding.",
         draw=draw_eu),
    dict(kicker="UNITED STATES", accent=SLATE,
         headline="STORM LASHES US EAST COAST ON BLACK FRIDAY",
         caption="56-mph gusts disrupt flights as Black Friday shoppers hunt deals.",
         draw=draw_storm),
    dict(kicker="MIDDLE EAST", accent=RED,
         headline="GAZA STRIKES KILL 10; DRONES KILL 2 IN KUWAIT",
         caption="Israeli strikes hit Gaza; Iran-linked drones kill two Italians in Kuwait.",
         draw=draw_gaza),
    dict(kicker="EGYPT", accent=BROWN,
         headline="CAIRO TANKER FIRE KILLS 31",
         caption="A fuel truck overturns on Cairo's ring road; the driver is detained.",
         draw=draw_cairo),
    dict(kicker="ASIA - TRADE", accent=TEAL,
         headline="VIETNAM RACES FOR US TRADE DEAL",
         caption="Hanoi seeks a deal before US tariffs of up to 35% hit clothing exports.",
         draw=draw_vietnam),
    dict(kicker="UNITED KINGDOM", accent=RED,
         headline="LONDON TUBE DRIVERS BEGIN 8-DAY STRIKE",
         caption="Tube drivers walk out for eight days of winter strikes across London.",
         draw=draw_tube),
]


def draw_panel(cv, px, py, pw, ph, p):
    cv.rect(px, py, px + pw, py + ph, WHITE)
    # border
    cv.rect(px, py, px + pw, py + 2, INK)
    cv.rect(px, py + ph - 2, px + pw, py + ph, INK)
    cv.rect(px, py, px + 2, py + ph, INK)
    cv.rect(px + pw - 2, py, px + pw, py + ph, INK)
    # kicker bar
    cv.rect(px + 2, py + 2, px + pw - 2, py + 28, p['accent'])
    cv.text(px + 12, py + 8, p['kicker'], 2, WHITE)
    # illustration
    ix0, iy0, ix1, iy1 = px + 10, py + 34, px + pw - 10, py + 152
    p['draw'](cv, ix0, iy0, ix1, iy1)
    cv.rect(ix0, iy0, ix1, iy0 + 2, INK)
    cv.rect(ix0, iy1 - 2, ix1, iy1, INK)
    # headline (2 lines max, scale 3)
    lines = wrap(p['headline'], 25)
    hy = py + 162
    for ln in lines[:2]:
        cv.text(px + 14, hy, ln, 3, INK)
        hy += 26
    # caption (scale 2)
    clines = wrap(p['caption'], 38)
    cy = py + 218
    for ln in clines[:2]:
        cv.text(px + 14, cy, ln, 2, GREY)
        cy += 18


# ------------------------------------------------------------------ build
def build():
    cv = Canvas(W, H, CREAM)
    # header
    cv.rect(0, 0, W, 118, NAVY)
    cv.rect(0, 118, W, 122, GOLD)
    cv.text(24, 16, "THE WORLD", 7, WHITE)
    cv.text(24, 74, "FRIDAY 27 NOVEMBER 2026", 3, GOLD)
    cv.text_right(W - 24, 22, "THE DAY IN", 2, WHITE)
    cv.text_right(W - 24, 44, "ONE IMAGE", 2, WHITE)
    cv.text_right(W - 24, 74, "SIX STORIES", 2, GOLD)
    # grid: 2 cols x 3 rows
    xs = [16, 518]
    ys = [130, 415, 700]
    pw, ph = 490, 273
    for i, p in enumerate(PANELS):
        draw_panel(cv, xs[i % 2], ys[i // 2], pw, ph, p)
    # footer
    cv.rect(0, 986, W, H, NAVY)
    cv.text_center(W // 2, 1000, "27 NOVEMBER 2026 - WORLD NEWS IN ONE IMAGE", 2, WHITE)
    return cv


# -------------------------------------------------------------------- png
def chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    n = write_png(cv, os.path.join(out_dir, "entry.png"))
    print(f"wrote {out_dir}/entry.png ({n} bytes)")


if __name__ == "__main__":
    main()
