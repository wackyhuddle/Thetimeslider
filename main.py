import pygame
import sys
import threading
import math
import os
import requests
from io import BytesIO
from db_lookup import lookup

pygame.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Time Slider")
clock = pygame.time.Clock()

MAP_W = 800
MAP_H = 600
TILE_SIZE = 256

# ─── MAP STYLES ───────────────────────────────────────────────────────────────

MAP_STYLES = {
    "modern": {
        "url":   "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        "label": "Modern Map (1900–present)",
    },
    "historical": {
        # OpenStreetMap humanitarian style — warm earthy tones, works great for historical feel
        "url":   "https://tile-a.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        "label": "Historical Map (1500–1899)",
    },
    "ancient": {
        # CartoDB Positron — clean light map, good for ancient era overlay
        "url":   "https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
        "label": "Ancient Map (before 1500)",
    },
}

def get_style_key(year):
    if year >= 1900:
        return "modern"
    elif year >= 1500:
        return "historical"
    else:
        return "ancient"

TILE_FOLDER = "tile_cache"
os.makedirs(TILE_FOLDER, exist_ok=True)
TILE_HEADERS = {"User-Agent": "TimeSlider/1.0"}

# ─── TILE CACHE ───────────────────────────────────────────────────────────────
TILE_CACHE    = {}        # (style, z, x, y) -> Surface
tile_lock     = threading.Lock()
tiles_loading = set()

# ─── MAP RENDER CACHE ─────────────────────────────────────────────────────────
# Only re-render the map surface when something actually changes
map_surface_cache   = None
last_render_state   = None   # (center_lat, center_lon, zoom, style_key)
map_dirty           = True   # force redraw on first frame

# ─── COLORS -------------------------------------------------------------------
BG        = (8,  12,  28)
PANEL_BG  = (15, 20,  45)
ACCENT    = (255, 200, 50)
ACCENT2   = (80,  180, 255)
WHITE     = (230, 230, 230)
GRAY      = (130, 130, 160)
RED       = (220, 60,  60)
BORDER    = (40,  50,  80)
GREEN     = (50,  200, 100)
GOLD      = (255, 180, 0)
SOFT_BLUE = (100, 160, 220)
ERA_COLORS = {
    "modern":     (20,  80,  160),
    "historical": (120, 70,  20),
    "ancient":    (70,  35,  10),
}

# ─── FONTS --------------------------------------------------------------------
font_title = pygame.font.SysFont("Georgia", 22, bold=True)
font_med   = pygame.font.SysFont("Georgia", 16, bold=True)
font_small = pygame.font.SysFont("Arial",   13)
font_year  = pygame.font.SysFont("Georgia", 38, bold=True)
font_label = pygame.font.SysFont("Arial",   12)

# ─── MAP STATE ----------------------------------------------------------------
map_center_lat = 20.0
map_center_lon = 0.0
map_zoom       = 2
MIN_ZOOM, MAX_ZOOM = 2, 16

panning          = False
pan_start_screen = (0, 0)
pan_start_lat    = 20.0
pan_start_lon    = 0.0

touch_fingers    = {}
pinch_start_dist = None
pinch_start_zoom = 2

# ─── GAME STATE ---------------------------------------------------------------
selected_year  = 1900
min_year       = -3000
max_year       = 2025
clicked_latlon = None
current_data   = None
status_msg     = "Click anywhere on the map"
loading        = False
dot_frame      = 0
prev_style_key = "modern"

SLIDER_X, SLIDER_Y = 30, MAP_H + 45
SLIDER_W, SLIDER_H = MAP_W - 60, 8
dragging_slider    = False

PANEL_X = MAP_W + 10
PANEL_W = WIDTH - PANEL_X - 10
PANEL_Y, PANEL_H = 10, HEIGHT - 20

search_result = None
search_lock   = threading.Lock()

placeholder = pygame.Surface((TILE_SIZE, TILE_SIZE))
placeholder.fill((190, 180, 165))


# ─── TILE MATH ────────────────────────────────────────────────────────────────

def ll_to_tile_f(lat, lon):
    n     = 2 ** map_zoom
    x     = (lon + 180.0) / 360.0 * n
    lat_r = math.radians(max(-85.05, min(85.05, lat)))
    y     = (1.0 - math.log(math.tan(lat_r) + 1.0 / math.cos(lat_r)) / math.pi) / 2.0 * n
    return x, y

def screen_to_ll(sx, sy):
    cx_f, cy_f = ll_to_tile_f(map_center_lat, map_center_lon)
    n  = 2 ** map_zoom
    tx = cx_f + (sx - MAP_W // 2) / TILE_SIZE
    ty = cy_f + (sy - MAP_H // 2) / TILE_SIZE
    lon = tx / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * ty / n))))
    return round(lat, 5), round(lon, 5)

def ll_to_screen(lat, lon):
    cx_f, cy_f = ll_to_tile_f(map_center_lat, map_center_lon)
    tx, ty     = ll_to_tile_f(lat, lon)
    return MAP_W//2 + (tx - cx_f)*TILE_SIZE, MAP_H//2 + (ty - cy_f)*TILE_SIZE



# ─── MBTILES DATABASE ─────────────────────────────────────────────────────────
import sqlite3 as _sq3
MBTILES_PATH = "world.mbtiles"
mbtiles_conn = None
mbtiles_lock = threading.Lock()

if os.path.exists(MBTILES_PATH):
    mbtiles_conn = _sq3.connect(MBTILES_PATH, check_same_thread=False)
    print(f"Loaded MBTiles: {MBTILES_PATH}")
else:
    print("No world.mbtiles found - using network. Run build_mbtiles.py first.")

def get_tile_from_mbtiles(style_key, z, x, y):
    if mbtiles_conn is None:
        return None
    try:
        with mbtiles_lock:
            row = mbtiles_conn.execute(
                "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=? AND style=?",
                (z, x, y, style_key)
            ).fetchone()
        if row:
            return pygame.image.load(BytesIO(bytes(row[0]))).convert()
    except Exception:
        pass
    return None


# ─── TILE LOADING ─────────────────────────────────────────────────────────────

def fetch_tile_bg(style_key, url_tmpl, z, x, y):
    global map_dirty
    key  = (style_key, z, x, y)
    path = os.path.join(TILE_FOLDER, f"{style_key}_{z}_{x}_{y}.png")
    try:
        if os.path.exists(path):
            surf = pygame.image.load(path).convert()
        else:
            r = requests.get(url_tmpl.format(z=z, x=x, y=y),
                             headers=TILE_HEADERS, timeout=8)
            if r.status_code != 200:
                return
            with open(path, "wb") as f:
                f.write(r.content)
            surf = pygame.image.load(BytesIO(r.content)).convert()
        with tile_lock:
            TILE_CACHE[key] = surf
        map_dirty = True
    except Exception:
        pass
    finally:
        with tile_lock:
            tiles_loading.discard(key)

def get_tile(style_key, url_tmpl, z, x, y):
    key = (style_key, z, x, y)
    # 1. Memory cache
    with tile_lock:
        if key in TILE_CACHE:
            return TILE_CACHE[key]
    # 2. Local MBTiles (instant, no network)
    surf = get_tile_from_mbtiles(style_key, z, x, y)
    if surf:
        with tile_lock:
            TILE_CACHE[key] = surf
        return surf
    # 3. Network fallback
    with tile_lock:
        if key not in tiles_loading:
            tiles_loading.add(key)
            threading.Thread(
                target=fetch_tile_bg,
                args=(style_key, url_tmpl, z, x, y),
                daemon=True
            ).start()
    return None

# ─── MAP SURFACE RENDERING ────────────────────────────────────────────────────

def render_map_surface(style_key):
    """Build the map Surface from tiles. Called ONLY when something changes."""
    global map_surface_cache, last_render_state, map_dirty

    url_tmpl = MAP_STYLES[style_key]["url"]
    surf     = pygame.Surface((MAP_W, MAP_H))
    surf.fill((190, 180, 165))

    cx_f, cy_f = ll_to_tile_f(map_center_lat, map_center_lon)
    n          = 2 ** map_zoom
    tl_x_f     = cx_f - (MAP_W // 2) / TILE_SIZE
    tl_y_f     = cy_f - (MAP_H // 2) / TILE_SIZE
    tl_x       = int(math.floor(tl_x_f))
    tl_y       = int(math.floor(tl_y_f))
    ox         = int((tl_x_f - tl_x) * TILE_SIZE)
    oy         = int((tl_y_f - tl_y) * TILE_SIZE)
    tiles_x    = math.ceil(MAP_W / TILE_SIZE) + 2
    tiles_y    = math.ceil(MAP_H / TILE_SIZE) + 2

    all_loaded = True
    for ty_off in range(tiles_y):
        for tx_off in range(tiles_x):
            tx = (tl_x + tx_off) % n
            ty = tl_y + ty_off
            if ty < 0 or ty >= n:
                continue
            tile = get_tile(style_key, url_tmpl, map_zoom, tx, ty)
            if tile is None:
                all_loaded = False
                surf.blit(placeholder, (tx_off * TILE_SIZE - ox, ty_off * TILE_SIZE - oy))
            else:
                surf.blit(tile, (tx_off * TILE_SIZE - ox, ty_off * TILE_SIZE - oy))

    map_surface_cache = surf
    last_render_state = (map_center_lat, map_center_lon, map_zoom, style_key)
    map_dirty = not all_loaded   # keep dirty until all tiles loaded


# ─── YEAR / SLIDER ────────────────────────────────────────────────────────────

def year_to_sx(year):
    return int(SLIDER_X + (year - min_year) / (max_year - min_year) * SLIDER_W)

def sx_to_year(sx):
    ratio = (sx - SLIDER_X) / SLIDER_W
    return max(min_year, min(max_year, int(min_year + ratio * (max_year - min_year))))

def fmt_year(y):
    return f"{abs(y)} BC" if y < 0 else f"{y} AD"


# ─── DB LOOKUP ────────────────────────────────────────────────────────────────

def do_lookup(lat, lon, year):
    global search_result
    data = lookup(lat, lon, year)
    with search_lock:
        search_result = data

def trigger_lookup(lat, lon, year):
    global loading, status_msg, search_result
    with search_lock:
        search_result = None
    loading    = True
    status_msg = "Looking up..."
    threading.Thread(target=do_lookup, args=(lat, lon, year), daemon=True).start()


# ─── DRAW HELPERS ─────────────────────────────────────────────────────────────

def rrect(color, rect, r=10, alpha=None):
    if alpha is not None:
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=r)
        screen.blit(s, (rect[0], rect[1]))
    else:
        pygame.draw.rect(screen, color, rect, border_radius=r)

def wrapped(text, font, color, x, y, max_w, lh=18):
    words, line = text.split(), ""
    for word in words:
        test = line + word + " "
        if font.size(test)[0] < max_w:
            line = test
        else:
            screen.blit(font.render(line.rstrip(), True, color), (x, y))
            y += lh
            line = word + " "
            if y > PANEL_Y + PANEL_H - 20:
                return y
    if line:
        screen.blit(font.render(line.rstrip(), True, color), (x, y))
        y += lh
    return y

def stat_row(label, value, x, y, lc=GRAY, vc=WHITE):
    screen.blit(font_label.render(label.upper(), True, lc), (x, y))
    screen.blit(font_small.render(str(value),    True, vc), (x, y + 14))
    return y + 36

def pinch_dist(fingers):
    pts = list(fingers.values())
    if len(pts) < 2:
        return None
    dx, dy = pts[0][0]-pts[1][0], pts[0][1]-pts[1][1]
    return (dx*dx + dy*dy) ** 0.5


# ─── DRAW FUNCTIONS ───────────────────────────────────────────────────────────

def draw_map():
    global map_dirty, prev_style_key
    style_key = get_style_key(selected_year)

    # Force redraw when style changes
    if style_key != prev_style_key:
        map_dirty     = True
        prev_style_key = style_key

    state = (map_center_lat, map_center_lon, map_zoom, style_key)
    if map_dirty or last_render_state != state:
        render_map_surface(style_key)

    if map_surface_cache:
        screen.blit(map_surface_cache, (0, 0))

    # Era banner
    ec     = ERA_COLORS[style_key]
    banner = pygame.Surface((MAP_W, 26), pygame.SRCALPHA)
    banner.fill((*ec, 210))
    screen.blit(banner, (0, 0))
    screen.blit(font_label.render(
        f"  {MAP_STYLES[style_key]['label']}  —  Zoom {map_zoom}  |  scroll=zoom  drag=pan",
        True, WHITE), (6, 6))

    # Pin
    if clicked_latlon:
        sx, sy = ll_to_screen(*clicked_latlon)
        if 0 <= sx <= MAP_W and 0 <= sy <= MAP_H:
            isx, isy = int(sx), int(sy)
            pygame.draw.circle(screen, (0,0,0),  (isx+2, isy+2), 9)
            pygame.draw.circle(screen, RED,      (isx,   isy  ), 9)
            pygame.draw.circle(screen, ACCENT,   (isx,   isy  ), 9, 2)
            pygame.draw.circle(screen, ACCENT,   (isx,   isy  ), 17, 1)
            if current_data and not loading:
                lbl = font_small.render(current_data["name"], True, WHITE)
                lx  = min(isx + 14, MAP_W - lbl.get_width() - 6)
                ly  = max(isy - 22, 28)
                pygame.draw.rect(screen, (20,20,40), (lx-3, ly-2, lbl.get_width()+6, 18), border_radius=3)
                screen.blit(lbl, (lx, ly))


def draw_slider():
    sk  = get_style_key(selected_year)
    ec  = ERA_COLORS[sk]
    rrect(PANEL_BG, (10, MAP_H+4, MAP_W-20, HEIGHT-MAP_H-8), r=10)
    pygame.draw.rect(screen, ec, (10, MAP_H+4, MAP_W-20, 4), border_radius=10)

    y_surf = font_year.render(fmt_year(selected_year), True, ACCENT)
    screen.blit(y_surf, (SLIDER_X, MAP_H+12))
    screen.blit(font_small.render(status_msg, True, GRAY),
                (SLIDER_X + y_surf.get_width() + 16, MAP_H+26))

    pygame.draw.rect(screen, BORDER, (SLIDER_X, SLIDER_Y, SLIDER_W, SLIDER_H), border_radius=4)
    fw = year_to_sx(selected_year) - SLIDER_X
    if fw > 0:
        pygame.draw.rect(screen, ACCENT2, (SLIDER_X, SLIDER_Y, fw, SLIDER_H), border_radius=4)

    hx, hy = year_to_sx(selected_year), SLIDER_Y + SLIDER_H//2
    pygame.draw.circle(screen, ACCENT, (hx, hy), 11)
    pygame.draw.circle(screen, BG,     (hx, hy),  6)

    for yr, lbl_txt in [(-3000,""),(1500,"Historical"),(1900,"Modern"),(2025,"")]:
        lx = year_to_sx(yr)
        pygame.draw.line(screen, ACCENT, (lx, SLIDER_Y-5), (lx, SLIDER_Y+SLIDER_H+5), 2)
        if lbl_txt:
            lb = font_label.render(lbl_txt, True, ACCENT)
            screen.blit(lb, (lx - lb.get_width()//2, SLIDER_Y-18))

    for yr in [-3000,-2000,-1000,0,500,1000,1500,1800,1900,2000,2025]:
        lx = year_to_sx(yr)
        pygame.draw.line(screen, GRAY, (lx, SLIDER_Y-3), (lx, SLIDER_Y+SLIDER_H+3), 1)
        lb = font_label.render(fmt_year(yr), True, GRAY)
        screen.blit(lb, (lx - lb.get_width()//2, SLIDER_Y+12))


def draw_panel():
    rrect(PANEL_BG, (PANEL_X, PANEL_Y, PANEL_W, PANEL_H), r=12)
    pygame.draw.rect(screen, BORDER, (PANEL_X, PANEL_Y, PANEL_W, PANEL_H), 1, border_radius=12)

    y, px, pw = PANEL_Y+16, PANEL_X+15, PANEL_W-30
    screen.blit(font_title.render("THE TIME SLIDER", True, ACCENT), (px, y))
    y += 34
    pygame.draw.line(screen, BORDER, (PANEL_X+10, y), (PANEL_X+PANEL_W-10, y), 1)
    y += 12

    if loading:
        dots = "." * ((dot_frame//15) % 4)
        screen.blit(font_med.render(f"Loading{dots}", True, ACCENT2), (px, y))
        return

    if not current_data:
        for txt, col in [
            ("HOW TO USE", ACCENT),   ("",WHITE),
            ("Click map to explore",  GRAY),
            ("any country in history.",GRAY), ("",WHITE),
            ("Map auto-switches:",     GRAY),
            ("1900+   Modern map",     GREEN),
            ("1500–1899 Historical",   GOLD),
            ("Before 1500  Ancient",   SOFT_BLUE), ("",WHITE),
            ("CONTROLS:", ACCENT),
            ("Scroll  = zoom",        GRAY),
            ("Drag    = pan",         GRAY),
            ("UP/DOWN = ±1 year",     GRAY),
            ("PgUp/Dn = ±100 years",  GRAY),
        ]:
            screen.blit(font_small.render(txt, True, col), (px, y))
            y += 20
        return

    screen.blit(font_med.render(current_data["name"], True, ACCENT2), (px, y));  y += 26
    screen.blit(font_small.render(f"Viewing: {fmt_year(selected_year)}", True, GREEN), (px, y)); y += 22
    pygame.draw.line(screen, BORDER, (PANEL_X+10, y), (PANEL_X+PANEL_W-10, y), 1); y += 10

    y = stat_row("Ruler / Leader",  current_data.get("ruler") or "Unknown",        px, y, GRAY, GOLD)
    y = stat_row("Est. Population", current_data.get("population_str","Unknown"),   px, y, GRAY, SOFT_BLUE)
    pygame.draw.line(screen, BORDER, (PANEL_X+10, y), (PANEL_X+PANEL_W-10, y), 1); y += 10

    events = current_data.get("events")
    if events:
        screen.blit(font_label.render("KEY EVENTS", True, GRAY), (px, y)); y += 14
        y = wrapped(events, font_small, WHITE, px, y, pw)
        y += 6
        pygame.draw.line(screen, BORDER, (PANEL_X+10, y), (PANEL_X+PANEL_W-10, y), 1); y += 10

    summary = current_data.get("summary")
    if summary:
        screen.blit(font_label.render("ABOUT", True, GRAY), (px, y)); y += 14
        wrapped(summary, font_small, WHITE, px, y, pw)


# ─── MAIN LOOP ────────────────────────────────────────────────────────────────

running = True
while running:
    clock.tick(60)
    dot_frame += 1
    mx, my = pygame.mouse.get_pos()

    with search_lock:
        if search_result is not None:
            current_data  = search_result
            search_result = None
            loading       = False
            status_msg    = f"Showing: {current_data['name']}"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.MOUSEWHEEL and 0 <= mx < MAP_W and 0 <= my < MAP_H:
            lat_c, lon_c = screen_to_ll(mx, my)
            map_zoom = max(MIN_ZOOM, min(MAX_ZOOM, map_zoom + (1 if event.y > 0 else -1)))
            sx2, sy2 = ll_to_screen(lat_c, lon_c)
            map_center_lat, map_center_lon = screen_to_ll(
                mx + (MAP_W//2 - sx2), my + (MAP_H//2 - sy2))
            map_center_lat = max(-85.0, min(85.0, map_center_lat))
            map_center_lon = max(-180.0, min(180.0, map_center_lon))
            map_dirty = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hx, hy = year_to_sx(selected_year), SLIDER_Y + SLIDER_H//2
            if abs(mx-hx)<16 and abs(my-hy)<16:
                dragging_slider = True
            elif SLIDER_X<=mx<=SLIDER_X+SLIDER_W and MAP_H+4<=my<=HEIGHT:
                selected_year = sx_to_year(mx)
                dragging_slider = True
            elif 0<=mx<MAP_W and 0<=my<MAP_H:
                panning = True
                pan_start_screen = (mx, my)
                pan_start_lat, pan_start_lon = map_center_lat, map_center_lon

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragging_slider and clicked_latlon:
                trigger_lookup(*clicked_latlon, selected_year)
            dragging_slider = False
            if panning:
                panning = False
                dx, dy = mx - pan_start_screen[0], my - pan_start_screen[1]
                if abs(dx)<5 and abs(dy)<5 and 0<=mx<MAP_W and 0<=my<MAP_H:
                    clicked_latlon = screen_to_ll(mx, my)
                    trigger_lookup(*clicked_latlon, selected_year)

        if event.type == pygame.MOUSEMOTION:
            if dragging_slider:
                selected_year = sx_to_year(mx)
            elif panning and 0<=mx<MAP_W:
                dx, dy = mx-pan_start_screen[0], my-pan_start_screen[1]
                nlat, nlon = screen_to_ll(MAP_W//2-dx, MAP_H//2-dy)
                slat, slon = screen_to_ll(MAP_W//2, MAP_H//2)
                map_center_lat = max(-85.0, min(85.0, pan_start_lat+(slat-nlat)))
                map_center_lon = max(-180.0, min(180.0, pan_start_lon+(slon-nlon)))
                map_dirty = True

        if event.type == pygame.FINGERDOWN:
            touch_fingers[event.finger_id] = (event.x*MAP_W, event.y*MAP_H)
            if len(touch_fingers)==2:
                pinch_start_dist = pinch_dist(touch_fingers)
                pinch_start_zoom = map_zoom

        if event.type == pygame.FINGERUP:
            touch_fingers.pop(event.finger_id, None)
            pinch_start_dist = None

        if event.type == pygame.FINGERMOTION:
            touch_fingers[event.finger_id] = (event.x*MAP_W, event.y*MAP_H)
            if len(touch_fingers)==2 and pinch_start_dist:
                nd = pinch_dist(touch_fingers)
                if nd and pinch_start_dist>0:
                    map_zoom = max(MIN_ZOOM, min(MAX_ZOOM,
                        int(round(pinch_start_zoom + math.log2(nd/pinch_start_dist)))))
                    map_dirty = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_year = min(max_year, selected_year+1)
            elif event.key == pygame.K_DOWN:
                selected_year = max(min_year, selected_year-1)
            elif event.key == pygame.K_PAGEUP:
                selected_year = min(max_year, selected_year+100)
            elif event.key == pygame.K_PAGEDOWN:
                selected_year = max(min_year, selected_year-100)

        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                if clicked_latlon:
                    trigger_lookup(*clicked_latlon, selected_year)

    screen.fill(BG)
    draw_map()
    draw_slider()
    draw_panel()
    pygame.display.flip()

pygame.quit()
sys.exit()