# Runs in the GitHub Action before the screenshot. Writes, when it can:
#   photo.png       262x364 portrait photo for the right-hand panel (weekdays)
#   photo_wide.png  800x480 landscape photo for the full-screen Shabbat view
#   shabbat.json    this week's candle-lighting / havdalah times from Hebcal
# Only photos whose shape already fits the frame are used, so nothing gets awkwardly cropped.
# A different photo is chosen every hour. If anything fails, the page falls back gracefully.
import io, json, re, sys, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from PIL import Image, ImageEnhance, ImageOps

ALBUM = "https://photos.app.goo.gl/VMJ2V5y3sFzX3j5z9"
TZ = ZoneInfo("America/New_York")
HEBCAL_GEONAMEID = 4180439          # Atlanta, GA — change for a different city (geonames.org id)
PANEL = (262, 364)                  # weekday photo box
WIDE = (800, 480)                   # Shabbat full screen
PORTRAIT_RATIOS = (0.55, 0.90)      # width/height range that fits the panel well
LANDSCAPE_RATIOS = (1.30, 2.00)     # width/height range that fits the full screen well
CHANGE_EVERY_HOURS = 1
PALETTE = [(0,0,0),(255,255,255),(208,32,26),(242,197,0),(28,138,60),(27,79,191)]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()

def album_photos():
    """[(url, width, height)] for every photo in the shared album."""
    html = get(ALBUM).decode("utf-8", "ignore")
    # Photo entries look like ["https://lh3.googleusercontent.com/pw/AP1Gcz...",4032,3024,...
    seen, out = set(), []
    for u, w, h in re.findall(r'\["(https://lh3\.googleusercontent\.com/pw/[^"]+)",(\d+),(\d+)', html):
        w, h = int(w), int(h)
        if u not in seen and w > 300 and h > 300:
            seen.add(u); out.append((u, w, h))
    return out

def dither(img):
    pal = Image.new("P", (1, 1))
    flat = [c for rgb in PALETTE for c in rgb]
    pal.putpalette(flat + flat[:3] * (256 - len(PALETTE)))
    return img.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")

def make(photos, ratios, size, out, salt):
    fits = [p for p in photos if ratios[0] <= p[1] / p[2] <= ratios[1]]
    print(f"{out}: {len(fits)} of {len(photos)} photos fit {size[0]}x{size[1]}")
    if not fits:
        return
    slot = int(datetime.now(TZ).timestamp() // (3600 * CHANGE_EVERY_HOURS))
    url = fits[(slot * 7919 + salt) % len(fits)][0]
    img = Image.open(io.BytesIO(get(url + "=w1600-h1600")))
    img = ImageOps.exif_transpose(img).convert("RGB")
    img = ImageOps.fit(img, size, Image.Resampling.LANCZOS, centering=(0.5, 0.4))
    img = ImageEnhance.Color(img).enhance(1.4)        # e-ink colors are muted; push them a bit
    img = ImageEnhance.Contrast(img).enhance(1.15)
    dither(img).save(out, optimize=True)

def shabbat():
    now = datetime.now(TZ)
    fri = now.date() + timedelta(days=(4 - now.weekday()) % 7)   # this week's Friday (Sat -> yesterday)
    if now.weekday() == 5:
        fri = now.date() - timedelta(days=1)
    url = (f"https://www.hebcal.com/shabbat?cfg=json&geonameid={HEBCAL_GEONAMEID}&M=on"
           f"&gy={fri.year}&gm={fri.month}&gd={fri.day}")
    items = json.loads(get(url)).get("items", [])
    pick = lambda cat: next((i for i in items if i.get("category") == cat), None)
    c, h, p = pick("candles"), pick("havdalah"), pick("parashat")
    data = {"candles": c and c["date"], "havdalah": h and h["date"],
            "parasha": p and p.get("title"), "location": HEBCAL_GEONAMEID}
    json.dump(data, open("shabbat.json", "w"))
    print("shabbat.json", data)

if __name__ == "__main__":
    for step in (shabbat,):
        try: step()
        except Exception as e: print("shabbat times skipped:", e, file=sys.stderr)
    try:
        photos = album_photos()
        print(f"found {len(photos)} photos in the album")
        make(photos, PORTRAIT_RATIOS, PANEL, "photo.png", 0)
        make(photos, LANDSCAPE_RATIOS, WIDE, "photo_wide.png", 3)
    except Exception as e:
        print("photo skipped:", e, file=sys.stderr)
