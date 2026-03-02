import sqlite3
import math
from geopy.geocoders import Nominatim

DB_PATH    = "history.db"
geolocator = Nominatim(user_agent="timeslider_lookup")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─── COUNTRY NAME FROM COORDINATES ───────────────────────────────────────────

def get_country_from_latlon(lat, lon):
    """
    Use reverse geocoding to get the actual country name at a lat/lon.
    Falls back to nearest-capital distance if geocoding fails.
    """
    try:
        result = geolocator.reverse(
            f"{lat}, {lon}",
            language="en",
            timeout=8,
            zoom=5          # country-level zoom
        )
        if result:
            addr    = result.raw.get("address", {})
            country = addr.get("country", "")
            state   = addr.get("state", "")
            city    = addr.get("city") or addr.get("town") or addr.get("village") or ""

            print(f"  Geocoded: city={city} state={state} country={country}")
            return country, state, city
    except Exception as e:
        print(f"  Geocode error: {e}")
    return None, None, None


# ─── FIND LOCATION IN DATABASE ────────────────────────────────────────────────

def find_location_by_name(country_name):
    """Look up a country in the database by name, with fuzzy fallbacks."""
    if not country_name:
        return None

    conn   = get_connection()
    cursor = conn.cursor()

    # 1. Exact match
    cursor.execute("SELECT * FROM locations WHERE name = ?", (country_name,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return dict(row)

    # 2. Case-insensitive match
    cursor.execute("SELECT * FROM locations WHERE LOWER(name) = LOWER(?)", (country_name,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return dict(row)

    # 3. Partial match — country name contains our search term
    cursor.execute("SELECT * FROM locations WHERE name LIKE ?", (f"%{country_name}%",))
    row = cursor.fetchone()
    if row:
        conn.close()
        return dict(row)

    # 4. Our search term contains the db name (e.g. "United States of America" → "United States")
    cursor.execute("SELECT id, name FROM locations")
    all_locs = cursor.fetchall()
    conn.close()

    country_lower = country_name.lower()
    for loc in all_locs:
        if loc["name"].lower() in country_lower:
            conn2 = get_connection()
            c2    = conn2.cursor()
            c2.execute("SELECT * FROM locations WHERE id=?", (loc["id"],))
            result = dict(c2.fetchone())
            conn2.close()
            return result

    return None


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def find_nearest_location_fallback(lat, lon):
    """Last resort: find closest location by capital distance."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM locations WHERE lat IS NOT NULL AND lon IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()

    closest, closest_dist = None, float("inf")
    for row in rows:
        dist = haversine(lat, lon, row["lat"], row["lon"])
        if dist < closest_dist:
            closest_dist = dist
            closest      = dict(row)
    return closest


# ─── GET HISTORY FOR A LOCATION + YEAR ────────────────────────────────────────

def get_history_for_year(location_id, year):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM history WHERE location_id=? ORDER BY year ASC",
        (location_id,)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not rows:
        return None

    result = {
        "summary": None, "ruler": None, "empire": None,
        "population": None, "appearance": None, "events": None,
    }

    # RULER — only within 50 years
    best_ruler_dist = 50
    for row in rows:
        if row["ruler"] and row["year"] != 0:
            dist = abs(row["year"] - year)
            if dist < best_ruler_dist:
                best_ruler_dist = dist
                result["ruler"] = row["ruler"]

    # EVENTS — only within 25 years
    best_event_dist = 25
    for row in rows:
        if row["events"] and row["year"] != 0:
            dist = abs(row["year"] - year)
            if dist < best_event_dist:
                best_event_dist = dist
                result["events"] = row["events"]

    # POPULATION — closest available
    best_pop_dist = float("inf")
    for row in rows:
        if row["population"] and row["year"] != 0:
            dist = abs(row["year"] - year)
            if dist < best_pop_dist:
                best_pop_dist = dist
                result["population"] = row["population"]

    # SUMMARY — prefer general (year=0), fall back to closest
    for row in rows:
        if row["year"] == 0:
            result["summary"]    = row["summary"]
            result["appearance"] = row["appearance"]
            break
    if not result["summary"]:
        best_s = float("inf")
        for row in rows:
            if row["summary"] and row["year"] != 0:
                dist = abs(row["year"] - year)
                if dist < best_s:
                    best_s = dist
                    result["summary"] = row["summary"]

    return result


# ─── MAIN LOOKUP ──────────────────────────────────────────────────────────────

def lookup(lat, lon, year):
    """
    Main function called by the game.
    Uses reverse geocoding to find the actual country at these coordinates,
    then queries the database for historical info.
    """
    # Step 1: get real country from coordinates
    country, state, city = get_country_from_latlon(lat, lon)

    # Step 2: find that country in the database
    location = None
    if country:
        location = find_location_by_name(country)

    # Step 3: fallback to nearest capital if geocoding failed
    if not location:
        print(f"  Falling back to nearest capital for ({lat}, {lon})")
        location = find_nearest_location_fallback(lat, lon)

    if not location:
        return {
            "name":           "Unknown Location",
            "summary":        "No data available for this area.",
            "ruler":          None,
            "empire":         None,
            "population":     None,
            "population_str": "Unknown",
            "appearance":     None,
            "events":         None,
        }

    # Step 4: get historical data for this location + year
    history = get_history_for_year(location["id"], year)

    result = {
        "name":       location["name"],
        "lat":        location.get("lat"),
        "lon":        location.get("lon"),
        "year":       year,
        "summary":    None,
        "ruler":      None,
        "empire":     None,
        "population": None,
        "appearance": None,
        "events":     None,
    }

    if history:
        result.update(history)

    # Format population
    pop = result.get("population")
    if pop:
        if pop >= 1_000_000_000:
            result["population_str"] = f"{pop/1_000_000_000:.1f}B"
        elif pop >= 1_000_000:
            result["population_str"] = f"{pop/1_000_000:.1f}M"
        elif pop >= 1_000:
            result["population_str"] = f"{pop/1_000:.0f}K"
        else:
            result["population_str"] = str(pop)
    else:
        result["population_str"] = "Unknown"

    return result


# ─── TEST ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        (40.7128,  -74.006,   1776, "New York → should be United States"),
        (51.5074,  -0.1278,   1940, "London → should be United Kingdom"),
        (48.8566,   2.3522,   1800, "Paris → should be France"),
        (35.6762,  139.6503,  1600, "Tokyo → should be Japan"),
        (45.4215,  -75.6919,  1900, "Ottawa → should be Canada"),
        (52.5200,   13.4050,  1943, "Berlin → should be Germany"),
        (-33.8688, 151.2093,  1900, "Sydney → should be Australia"),
        (55.7558,   37.6173,  1812, "Moscow → should be Russia"),
    ]

    for lat, lon, year, label in tests:
        print(f"\n{'='*50}")
        print(f"Test: {label}")
        result = lookup(lat, lon, year)
        print(f"  → Got: {result['name']}")
        print(f"     Ruler:      {result.get('ruler') or 'None'}")
        print(f"     Population: {result.get('population_str')}")