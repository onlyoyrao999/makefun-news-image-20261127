#!/usr/bin/env python3
"""One-page newspaper front page for 27 November 2026.

Draws a 1024x1024 PNG that sums up the day's world news in six stories:
tankers mined off Oman, Zelenskyy on the US looking to the Middle East,
the Houthi advance on Aden, a Thanksgiving storm flooding the US, Sanofi's
$41bn buyout of Insmed, and Bitcoin holding $60,000.

The picture is painted pixel by pixel with nothing but the Python
standard library: a tiny canvas, a hand-made 5x7 block font, and a small
PNG writer built on zlib and struct. No Pillow, no network, no fonts
from disk, no image files read in. The run is fully deterministic, so
two runs write byte-identical files.

Output: $MAKEFUN_OUTPUT when set, otherwise /output/entry.png.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024
SIZE_CAP = 1024 * 1024  # 1 MiB

# ---------------------------------------------------------------- palette
PAPER = (248, 244, 232)
INK = (26, 26, 26)
NAVY = (16, 36, 62)
NAVY_LIGHT = (31, 58, 95)
RED = (179, 38, 30)
GOLD = (201, 162, 39)
GOLD_LIGHT = (232, 196, 90)
SKY = (188, 214, 232)
SEA = (28, 78, 122)
WHITE = (255, 255, 255)
GREY = (120, 118, 110)
DARK_GREY = (64, 64, 64)
ORANGE = (232, 110, 24)
YELLOW = (250, 204, 21)
GREEN = (34, 120, 62)
TEAL = (14, 116, 118)
BROWN = (122, 82, 40)

# ------------------------------------------------------- 5x7 block font
# Each glyph is seven rows; each row is five bits, leftmost pixel first.
FONT = {
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    "_": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "\u2022": (0x00, 0x04, 0x0E, 0x0E, 0x0E, 0x04, 0x00),
}


class Page:
    """A plain RGB canvas with a few drawing helpers."""

    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.pixels = bytearray(background * (width * height))

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pixels[i] = color[0]
            self.pixels[i + 1] = color[1]
            self.pixels[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                self.pixels[base] = color[0]
                self.pixels[base + 1] = color[1]
                self.pixels[base + 2] = color[2]
                base += 3

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            half = thick // 2
            self.rect(x0 - half, y0 - half, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            half = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.rect(cx - half, yy, half * 2 + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=3):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - thick <= d <= r:
                    self._set(xx, yy, color)

    def burst(self, cx, cy, r, color, spikes=12):
        """A starburst: straight rays out from a filled centre."""
        self.disc(cx, cy, r // 3, color)
        for k in range(spikes):
            ang = 3.14159265 * 2 * k / spikes
            ex = cx + int(r * _cos(ang))
            ey = cy + int(r * _sin(ang))
            self.line(cx, cy, ex, ey, color, thick=4)

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, color, scale=2):
        s = s.upper()
        for ci, ch in enumerate(s):
            glyph = FONT.get(ch, FONT[" "])
            ox = x + ci * 6 * scale
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.rect(ox + col * scale, y + row * scale,
                                  scale, scale, color)
        return x + self.text_width(s, scale)

    def text_center(self, cx, y, s, color, scale=2):
        self.text(cx - self.text_width(s.upper(), scale) // 2, y, s,
                  color, scale)

    def wrap(self, s, max_width, scale):
        """Greedy word wrap; returns a list of lines that fit."""
        words = s.split()
        lines = []
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if self.text_width(trial, scale) <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def paragraph(self, x, y, s, color, scale, max_width, gap=4):
        for line in self.wrap(s, max_width, scale):
            self.text(x, y, line, color, scale)
            y += 7 * scale + gap
        return y


def _cos(a):
    # Cosine via the Taylor series, good enough for burst rays.
    a = a % 6.283185307179586
    total = 1.0
    term = 1.0
    for n in range(1, 8):
        term *= -a * a / ((2 * n - 1) * (2 * n))
        total += term
    return total


def _sin(a):
    return _cos(a - 1.5707963267948966)


# ------------------------------------------------------------ PNG writer
def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def encode_png(page):
    raw = bytearray()
    row_bytes = page.w * 3
    for y in range(page.h):
        raw.append(0)  # filter: none
        raw += page.pixels[y * row_bytes:(y + 1) * row_bytes]
    ihdr = struct.pack(">IIBBBBB", page.w, page.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            _chunk(b"IEND", b""))


# ------------------------------------------------------------ the stories
STORIES = [
    {
        "kicker": "THE GULF",
        "accent": RED,
        "headline": "TANKERS MINED OFF OMAN",
        "sub": "AS THE GULF WAR WIDENS",
        "body": [
            "MINES STRUCK SHIPS IN THE STRAIT OF HORMUZ",
            "OIL LANES ON EDGE AS THE CONFLICT SPREADS",
        ],
    },
    {
        "kicker": "KYIV",
        "accent": NAVY_LIGHT,
        "headline": "ZELENSKYY: US LOOKS AWAY",
        "body": "ZELENSKYY TELLS THE BBC: THE US IS TOO FOCUSED "
                "ON THE MIDDLE EAST",
    },
    {
        "kicker": "YEMEN",
        "accent": BROWN,
        "headline": "HOUTHIS PUSH ON ADEN",
        "body": "REBELS ADVANCE TOWARD THE PORT CITY AS THE FRONT "
                "LINE MOVES SOUTH",
    },
    {
        "kicker": "WEATHER",
        "accent": TEAL,
        "headline": "STORM FLOODS US",
        "body": "AT THANKSGIVING, RAIN SWAMPS CITIES COAST TO COAST "
                "AS HOLIDAY TRAVEL STALLS",
    },
    {
        "kicker": "MARKETS",
        "accent": GREEN,
        "headline": "SANOFI BUYS INSMED",
        "body": "$41BN: THE BIGGEST PHARMA DEAL OF THE YEAR",
    },
    {
        "kicker": "CRYPTO",
        "accent": GOLD,
        "headline": "BITCOIN HOLDS $60,000",
        "body": "DESPITE RECORD OUTFLOWS FROM FUNDS, THE COIN "
                "CLINGS TO THE BIG LEVEL",
    },
]


# ------------------------------------------------------------ illustrations
def draw_tanker_scene(p, x, y, w, h):
    """Sky, sea, a tanker, a mine and a blast off Oman."""
    p.rect(x, y, w, h, SKY)
    p.rect(x, y + h // 2 + 12, w, h - h // 2 - 12, SEA)
    p.disc(x + w - 90, y + 34, 26, GOLD_LIGHT)
    for cx, cy, r in ((x + 90, y + 30, 26), (x + 118, y + 38, 20),
                      (x + 66, y + 40, 16)):
        p.disc(cx, cy, r, WHITE)
    # Tanker hull, deck boxes and funnel.
    hull_y = y + h // 2 + 26
    p.rect(x + 60, hull_y, 340, 42, (32, 36, 42))
    p.line(x + 60, hull_y, x + 28, hull_y + 42, (32, 36, 42), thick=4)
    p.rect(x + 330, hull_y - 34, 56, 34, WHITE)
    p.rect(x + 348, hull_y - 52, 22, 18, RED)
    for i, c in enumerate((RED, GOLD, TEAL, GREEN)):
        p.rect(x + 92 + i * 56, hull_y - 26, 48, 26, c)
    # Waves.
    for wx in range(x + 20, x + w - 20, 52):
        p.line(wx, y + h - 26, wx + 30, y + h - 26, WHITE, thick=3)
    for wx in range(x + 40, x + w - 20, 64):
        p.line(wx, y + h - 12, wx + 26, y + h - 12, (150, 190, 220), thick=2)
    # A spiked mine floating near the ship.
    mx, my = x + 520, y + h - 46
    for k in range(8):
        ang = 3.14159265 * k / 4
        p.line(mx, my, mx + int(30 * _cos(ang)), my + int(30 * _sin(ang)),
               DARK_GREY, thick=4)
    p.disc(mx, my, 18, DARK_GREY)
    p.disc(mx - 5, my - 5, 5, GREY)
    # The blast: orange burst, yellow heart, grey smoke.
    bx, by = x + 660, y + 62
    p.burst(bx, by, 52, ORANGE, spikes=12)
    p.disc(bx, by, 20, YELLOW)
    for cx, cy, r in ((bx - 34, by - 42, 18), (bx + 8, by - 52, 22),
                      (bx + 40, by - 38, 15)):
        p.disc(cx, cy, r, (150, 150, 148))
    p.text(x + w - 250, y + h - 56, "STRAIT OF HORMUZ", WHITE, 2)


def draw_microphone(p, x, y):
    p.disc(x + 34, y + 22, 22, NAVY_LIGHT)
    p.disc(x + 34, y + 22, 13, WHITE)
    p.rect(x + 28, y + 44, 12, 34, DARK_GREY)
    p.line(x + 34, y + 78, x + 34, y + 96, DARK_GREY, thick=4)
    p.line(x + 16, y + 96, x + 52, y + 96, DARK_GREY, thick=4)
    p.rect(x + 66, y + 8, 40, 10, (0, 87, 184))
    p.rect(x + 66, y + 18, 40, 10, (255, 213, 0))


def draw_route_arrow(p, x, y):
    p.line(x + 14, y + 88, x + 82, y + 18, RED, thick=7)
    p.line(x + 82, y + 18, x + 58, y + 16, RED, thick=5)
    p.line(x + 82, y + 18, x + 82, y + 42, RED, thick=5)
    for dx, dy in ((10, 84), (30, 66), (50, 48), (70, 30)):
        p.disc(x + dx, y + dy, 5, BROWN)
    p.disc(x + 14, y + 88, 9, BROWN)
    p.rect(x + 64, y + 56, 52, 24, BROWN)
    p.text(x + 68, y + 63, "ADEN", WHITE, 2)


def draw_storm(p, x, y):
    for cx, cy, r in ((x + 30, y + 34, 22), (x + 56, y + 26, 28),
                      (x + 84, y + 36, 22)):
        p.disc(cx, cy, r, DARK_GREY)
    p.rect(x + 12, y + 44, 96, 16, DARK_GREY)
    for rx in (x + 22, x + 48, x + 74, x + 96):
        p.line(rx, y + 66, rx - 6, y + 88, TEAL, thick=3)
    p.line(x + 96, y + 60, x + 84, y + 76, YELLOW, thick=5)
    p.line(x + 84, y + 76, x + 96, y + 92, YELLOW, thick=5)


def draw_capsule(p, x, y):
    """A red-and-white capsule with rounded ends."""
    # Pale panel behind it, so the white half shows on a white cell.
    p.rect(x, y + 20, 118, 58, (236, 232, 220))
    p.rect(x + 8, y + 30, 92, 34, WHITE)
    p.rect(x + 8, y + 30, 46, 34, RED)
    p.disc(x + 8, y + 47, 17, RED)
    p.disc(x + 100, y + 47, 17, WHITE)


def draw_bitcoin(p, x, y):
    p.disc(x + 54, y + 48, 46, GOLD)
    p.ring(x + 54, y + 48, 46, (150, 110, 10), thick=4)
    p.text(x + 38, y + 26, "B", (120, 80, 0), 6)


# ------------------------------------------------------------ page layout
def draw_masthead(p):
    p.rect(0, 0, WIDTH, 122, NAVY)
    p.text_center(WIDTH // 2, 16, "FRIDAY  -  THE WORLD IN ONE PAGE",
                  GOLD_LIGHT, 3)
    p.text_center(WIDTH // 2, 52, "27 NOVEMBER 2026", WHITE, 7)
    p.rect(40, 112, WIDTH - 80, 4, GOLD)


def draw_lead(p):
    s = STORIES[0]
    p.rect(40, 140, WIDTH - 80, 356, WHITE)
    p.rect(40, 140, WIDTH - 80, 6, s["accent"])
    draw_tanker_scene(p, 56, 156, WIDTH - 112, 162)
    p.text(56, 332, s["kicker"] + "  -  LEAD STORY", s["accent"], 3)
    y = 366
    for line in p.wrap(s["headline"], WIDTH - 112, 6):
        p.text(56, y, line, INK, 6)
        y += 7 * 6 + 6
    p.text(56, y + 2, s["sub"], RED, 3)
    y += 7 * 3 + 12
    for line in s["body"]:
        p.text(56, y, line, DARK_GREY, 2)
        y += 7 * 2 + 6
    p.rect(40, 504, WIDTH - 80, 3, INK)


def draw_cell(p, x, y, w, h, story, draw_icon):
    p.rect(x, y, w, h, WHITE)
    p.rect(x, y, w, 5, story["accent"])
    chip = story["kicker"]
    pad = 10
    chip_w = p.text_width(chip, 2) + pad * 2
    p.rect(x + 16, y + 18, chip_w, 30, story["accent"])
    p.text(x + 16 + pad, y + 25, chip, WHITE, 2)
    # The picture sits in the top-right corner; the headline wraps
    # around it and the body runs full width underneath.
    draw_icon(p, x + w - 120, y + 12)
    scale = 4 if w > 320 else 3
    head_y = y + 58
    for line in p.wrap(story["headline"], w - 32 - 116, scale):
        p.text(x + 16, head_y, line, INK, scale)
        head_y += 7 * scale + 5
    body_y = head_y + 8
    for line in p.wrap(story["body"], w - 32, 2):
        p.text(x + 16, body_y, line, DARK_GREY, 2)
        body_y += 7 * 2 + 6


def draw_footer(p):
    p.rect(40, 962, WIDTH - 80, 2, GOLD)
    p.text_center(WIDTH // 2, 974,
                  "SIX STORIES  \u2022  ONE PAGE  \u2022  DRAWN BY CODE  "
                  "\u2022  27 NOVEMBER 2026",
                  GREY, 2)


def build_page():
    p = Page(WIDTH, HEIGHT, PAPER)
    draw_masthead(p)
    draw_lead(p)
    draw_cell(p, 40, 518, 452, 200, STORIES[1], draw_microphone)
    draw_cell(p, 532, 518, 452, 200, STORIES[2], draw_route_arrow)
    draw_cell(p, 40, 732, 304, 218, STORIES[3], draw_storm)
    draw_cell(p, 360, 732, 304, 218, STORIES[4], draw_capsule)
    draw_cell(p, 680, 732, 304, 218, STORIES[5], draw_bitcoin)
    draw_footer(p)
    return p


# ------------------------------------------------------------ verification
def verify(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("FAIL: not a PNG file")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (WIDTH, HEIGHT):
        raise SystemExit(f"FAIL: size is {width}x{height}, want 1024x1024")
    if len(data) > SIZE_CAP:
        raise SystemExit(f"FAIL: {len(data)} bytes, over the 1 MiB cap")
    print(f"OK: {path}  {width}x{height}  {len(data)} bytes  "
          f"(cap {SIZE_CAP})")


def main():
    page = build_page()
    png = encode_png(page)
    target = os.environ.get("MAKEFUN_OUTPUT") or "/output/entry.png"
    folder = os.path.dirname(target)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(target, "wb") as fh:
        fh.write(png)
    verify(target)


if __name__ == "__main__":
    main()
