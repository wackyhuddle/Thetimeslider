"""
build_mbtiles.py
Run this ONCE to download world tiles into a local MBTiles database.
After this runs, the game never needs the internet for map tiles.

Downloads zoom levels 0-7 (~22,000 tiles, ~150MB).
Zoom 8+ still uses network but gets cached to tile_cache/ as before.
"""

import sqlite3
import requests
import time
import math
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

OUTPUT   = "world.mbtiles"
HEADERS  = {"User-Agent": "TimeSlider/1.0 (history-game-project)"}
MAX_ZOOM = 7        # download 0-7 offline, 8+ loads from network as before
WORKERS  = 8        # parallel download threads

TILE_SOURCES = {
    "modern":     "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    "historical": "https://tile-a.openstreetmap.fr/hot/{z}/{x}/{y}.png",
    "ancient":    "https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
}

# ─── CREATE DATABASE ──────────────────────────────────────────────────────────

print("Creating MBTiles database...")
conn   = sqlite3.connect(OUTPUT)
cursor = conn.cursor()

cursor.executescript("""
    CREATE TABLE IF NOT EXISTS tiles (
        zoom_level  INTEGER,
        tile_column INTEGER,
        tile_row    INTEGER,
        style       TEXT,
        tile_data   BLOB,
        PRIMARY KEY (zoom_level, tile_column, tile_row, style)
    );
    CREATE TABLE IF NOT EXISTS metadata (
        name  TEXT,
        value TEXT
    );
""")

cursor.executemany("INSERT OR REPLACE INTO metadata VALUES (?,?)", [
    ("name",        "World Tiles"),
    ("format",      "png"),
    ("minzoom",     "0"),
    ("maxzoom",     str(MAX_ZOOM)),
])
conn.commit()
print("Database created.\n")


# ─── COUNT TILES TO DOWNLOAD ──────────────────────────────────────────────────

def tile_count(max_zoom):
    total = 0
    for z in range(max_zoom + 1):
        total += 4 ** z
    return total

total_per_style = tile_count(MAX_ZOOM)
total_all       = total_per_style * len(TILE_SOURCES)
print(f"Tiles per style: {total_per_style:,}")
print(f"Total tiles:     {total_all:,}  (3 styles × {total_per_style:,})")
print(f"Estimated size:  ~{total_all * 15 // 1024}MB\n")


# ─── DOWNLOAD FUNCTION ────────────────────────────────────────────────────────

def already_have(cursor, style, z, x, y):
    cursor.execute(
        "SELECT 1 FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=? AND style=?",
        (z, x, y, style)
    )
    return cursor.fetchone() is not None

def download_tile(style, url_tmpl, z, x, y):
    """Download one tile. Returns (style, z, x, y, data) or None on failure."""
    try:
        url  = url_tmpl.format(z=z, x=x, y=y)
        r    = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return (style, z, x, y, r.content)
    except Exception:
        pass
    return None


# ─── DOWNLOAD ALL TILES ───────────────────────────────────────────────────────

# Use a separate connection per thread for writing
write_lock = __import__("threading").Lock()

def write_tile(style, z, x, y, data):
    with write_lock:
        conn2 = sqlite3.connect(OUTPUT)
        conn2.execute(
            "INSERT OR REPLACE INTO tiles VALUES (?,?,?,?,?)",
            (z, x, y, style, sqlite3.Binary(data))
        )
        conn2.commit()
        conn2.close()

for style_name, url_tmpl in TILE_SOURCES.items():
    print(f"Downloading {style_name} tiles...")
    tasks     = []
    done      = 0
    skipped   = 0

    # Build task list
    for z in range(MAX_ZOOM + 1):
        n = 2 ** z
        for x in range(n):
            for y in range(n):
                # Check if already downloaded
                chk = conn.execute(
                    "SELECT 1 FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=? AND style=?",
                    (z, x, y, style_name)
                ).fetchone()
                if chk:
                    skipped += 1
                else:
                    tasks.append((style_name, url_tmpl, z, x, y))

    print(f"  {skipped} already cached, {len(tasks)} to download...")

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(download_tile, *t): t for t in tasks}
        for future in as_completed(futures):
            result = future.result()
            done  += 1
            if result:
                style, z, x, y, data = result
                write_tile(style, z, x, y, data)
            # Progress every 100 tiles
            if done % 100 == 0 or done == len(tasks):
                pct = done / max(len(tasks), 1) * 100
                print(f"  {done}/{len(tasks)}  ({pct:.0f}%)", end="\r")
            time.sleep(0.01)  # be polite to tile servers

    print(f"\n  Done with {style_name}!\n")

# ─── FINAL STATS ──────────────────────────────────────────────────────────────

count = conn.execute("SELECT COUNT(*) FROM tiles").fetchone()[0]
size  = os.path.getsize(OUTPUT) / 1024 / 1024
print(f"{'='*50}")
print(f"MBTiles database complete!")
print(f"  Tiles stored: {count:,}")
print(f"  File size:    {size:.1f} MB")
print(f"  Location:     {OUTPUT}")
print(f"\nYou can now run main.py — maps will load instantly!")
conn.close()