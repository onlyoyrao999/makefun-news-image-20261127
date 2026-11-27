#!/usr/bin/env python3
"""Draw the 27 November 2026 world-news front page (1024x1024 PNG, deterministic).

Same layout as the 23-25 Nov entries: masthead, lead panel, 2x2 story grid.
"""
from PIL import Image, ImageDraw, ImageFont
import os

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_wrapped(draw, x, y, text, fnt, fill, width, lh):
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y

def build(date_str, day_label, lead_kicker, lead_head, lead_body, stories, out_path, accent, also=""):
    W, H = 1024, 1024
    bg = (247, 243, 232)
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 118], fill=(16, 32, 64))
    d.text((36, 18), "THE WORLD  \u2022  IN ONE IMAGE", font=font(SANS_B, 26), fill=(255, 255, 255))
    d.text((36, 56), date_str, font=font(SANS_B, 34), fill=(255, 214, 90))
    d.text((W-36, 28), day_label, font=font(SANS, 22), fill=(200, 210, 230), anchor="ra")
    d.text((W-36, 60), "WORLD NEWS", font=font(SANS_B, 22), fill=(200, 210, 230), anchor="ra")
    d.rectangle([28, 138, W-28, 452], fill=(255, 255, 255), outline=accent, width=4)
    d.rectangle([28, 138, W-28, 182], fill=accent)
    d.text((48, 148), lead_kicker, font=font(SANS_B, 22), fill=(255, 255, 255))
    y = 198
    y = draw_wrapped(d, 48, y, lead_head, font(SERIF_B, 40), (16, 32, 64), W-96, 50)
    y += 8
    y = draw_wrapped(d, 48, y, lead_body, font(SANS, 24), (40, 40, 40), W-96, 32)
    if also:
        y += 12
        d.line([(48, y), (W-48, y)], fill=(200, 200, 190), width=2)
        y += 14
        draw_wrapped(d, 48, y, also, font(SANS_B, 21), (16, 32, 64), W-96, 28)
    x0, y0 = 28, 472
    cw, ch = 474, 236
    for i, (kicker, head, body, color) in enumerate(stories):
        x = x0 + (i % 2) * (cw + 20)
        yy = y0 + (i // 2) * (ch + 16)
        d.rectangle([x, yy, x+cw, yy+ch], fill=(255, 255, 255), outline=(180, 180, 170), width=2)
        d.rectangle([x, yy, x+10, yy+ch], fill=color)
        d.text((x+26, yy+14), kicker, font=font(SANS_B, 19), fill=color)
        y2 = draw_wrapped(d, x+26, yy+44, head, font(SERIF_B, 27), (16, 32, 64), cw-52, 33)
        draw_wrapped(d, x+26, y2+6, body, font(SANS, 20), (60, 60, 60), cw-52, 26)
    d.text((36, 986), "One image sums up the day.  Sources: Reuters / AP / AFP, public news reports.",
           font=font(SANS, 17), fill=(90, 90, 90))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    print(out_path, os.path.getsize(out_path))

build(
    "FRIDAY  \u2022  27 NOVEMBER 2026", "No. 27",
    "GULF  \u2022  LEAD STORY",
    "Tankers mined off Oman as war widens",
    "Iran says two oil tankers were hit by naval mines near Oman\u2019s Khasab port; Houthis push toward Aden and oil climbs past $95 a barrel.",
    [
        ("UKRAINE", "Zelenskyy: US looking away",
         "Zelenskyy tells the BBC the US is too focused on the Middle East; North Korea halts military aid to Russia; Ukraine hits a Russian Su-34 base.",
         (16, 80, 140)),
        ("YEMEN", "Houthis advance on Aden",
         "Houthi rebels push toward Yemen\u2019s government hub Aden after a refinery strike lifts oil prices.",
         (178, 34, 34)),
        ("USA", "Thanksgiving storm floods US",
         "A major storm brings flooding and flight delays; more than 800,000 customers lose power on the East Coast.",
         (0, 110, 90)),
        ("MARKETS", "Sanofi seals $41bn buyout",
         "Sanofi signs a $41bn cash deal for Insmed, the year\u2019s biggest biopharma buyout; Bitcoin holds $60,000 amid record outflows.",
         (120, 70, 20)),
    ],
    "/home/hatch/workspace/makefun/repos36/makefun-news-image-20261127/entry.png",
    (178, 34, 34),
    also="Also today: Two Italians killed in Kuwait strike  \u2022  Tanker off Ibiza capsizes, one dead  \u2022  NZ coalition one seat short  \u2022  SpaceX gets satellite approval",
)
print("done27")
