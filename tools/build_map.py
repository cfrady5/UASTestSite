#!/usr/bin/env python3
"""
Build assets/js/map-data.js — the geometry and tables the capabilities map draws.

    python3 tools/build_map.py

Reads the committed extracts in tools/geo-src/ (see fetch_geo.py) plus the
shared tables in site_data.py, projects everything into one SVG coordinate
space, and writes a single JavaScript file. Nothing is projected in the browser.

Projection
----------
Albers equal-area conic, standard parallels 38°N and 41.5°N, origin 39.75°N
86.45°W. That is the usual choice for a single mid-latitude US state: it keeps
areas honest, and across four degrees of latitude the shape distortion is not
visible. Everything on the map — outline, counties, roads, rivers, markers —
goes through the same projection, so they register against each other exactly.

The state outline is DERIVED from the county polygons by keeping the edges that
belong to only one county. Census cartographic boundary files share identical
coordinates along shared borders, so this is an exact dissolve: the outline is
the county layer's own perimeter, not a separate file that might not line up.
"""

import json
import math
import pathlib
from collections import Counter, defaultdict

import site_data

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "geo-src"
OUT = ROOT / "assets" / "js" / "map-data.js"

# --- Projection parameters -------------------------------------------------
LAT0, LON0 = 39.75, -86.45
LAT1, LAT2 = 38.0, 41.5

# --- Output space ----------------------------------------------------------
WIDTH = 1000.0          # SVG user units across the full extent
PAD = 18.0              # keeps out-of-state markers and labels off the edge

# Simplification tolerance, in SVG user units. The map renders at roughly
# 560–760 CSS px wide, so one unit is well under a pixel and 0.08 is invisible.
TOL = {"counties": 0.09, "roads": 0.12, "rivers": 0.12, "lakes": 0.12}


# ---------------------------------------------------------------------------
# Albers equal-area conic
# ---------------------------------------------------------------------------
_rad = math.radians
_n = (math.sin(_rad(LAT1)) + math.sin(_rad(LAT2))) / 2.0
_C = math.cos(_rad(LAT1)) ** 2 + 2 * _n * math.sin(_rad(LAT1))
_rho0 = math.sqrt(_C - 2 * _n * math.sin(_rad(LAT0))) / _n


def project(lon, lat):
    """(lon, lat) in degrees -> (x, y) in projection units, y up."""
    theta = _n * (_rad(lon) - _rad(LON0))
    rho = math.sqrt(_C - 2 * _n * math.sin(_rad(lat))) / _n
    return rho * math.sin(theta), _rho0 - rho * math.cos(theta)


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def simplify(points, tol):
    """Douglas–Peucker. Keeps endpoints; tol is a perpendicular distance."""
    if len(points) < 3:
        return points

    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]

    while stack:
        lo, hi = stack.pop()
        if hi <= lo + 1:
            continue
        ax, ay = points[lo]
        bx, by = points[hi]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy)

        worst, worst_i = -1.0, lo
        for i in range(lo + 1, hi):
            px, py = points[i]
            if norm == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dy * px - dx * py + bx * ay - by * ax) / norm
            if d > worst:
                worst, worst_i = d, i

        if worst > tol:
            keep[worst_i] = True
            stack.append((lo, worst_i))
            stack.append((worst_i, hi))

    return [p for p, k in zip(points, keep) if k]


def path_d(rings, close, tol, decimals=1):
    """Rings of (x, y) -> an SVG path string."""
    parts = []
    for ring in rings:
        pts = simplify(ring, tol) if tol else ring
        if len(pts) < 2:
            continue
        out = [f"M{round(pts[0][0], decimals)} {round(pts[0][1], decimals)}"]
        prev = pts[0]
        for x, y in pts[1:]:
            # Drop a vertex that rounds onto the previous one
            if (round(x, decimals), round(y, decimals)) == \
               (round(prev[0], decimals), round(prev[1], decimals)):
                continue
            out.append(f"L{round(x, decimals)} {round(y, decimals)}")
            prev = (x, y)
        if close:
            out.append("Z")
        parts.append("".join(out))
    return "".join(parts)


def declutter(points, min_sep, rounds=260):
    """Push overlapping markers apart, the way a cartographer displaces
    co-located symbols.

    Several of these markers sit on top of each other — the 38th Infantry
    Division and 81st Troop Command share Stout Field exactly, and NSWC Crane
    and Crane Army Ammunition Activity are a few kilometres apart, which is
    under a marker's width at this scale. Left alone they cannot be told apart
    or clicked individually.

    This moves only the display position. The latitude and longitude published
    in the detail panel stay exactly as sourced, and any marker that moved is
    flagged so the panel can say so.
    """
    pos = [list(p) for p in points]
    for r in range(rounds):
        moved = False
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dx = pos[j][0] - pos[i][0]
                dy = pos[j][1] - pos[i][1]
                d = math.hypot(dx, dy)
                if d >= min_sep:
                    continue
                if d < 1e-6:
                    # Exactly coincident: separate along a stable direction so
                    # the output does not change between runs.
                    ang = (i * 2.399963)          # golden angle, radians
                    dx, dy, d = math.cos(ang), math.sin(ang), 1.0
                push = (min_sep - d) / 2.0
                ux, uy = dx / d, dy / d
                pos[i][0] -= ux * push
                pos[i][1] -= uy * push
                pos[j][0] += ux * push
                pos[j][1] += uy * push
                moved = True
        if not moved:
            break
    return pos


def centroid(ring):
    """Area centroid of a closed ring of (x, y)."""
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    if a == 0:                       # degenerate: fall back to the mean
        n = len(ring)
        return sum(p[0] for p in ring) / n, sum(p[1] for p in ring) / n
    return cx / (3 * a), cy / (3 * a)


def rings_of(geom):
    """Polygon / MultiPolygon / LineString / MultiLineString -> list of rings."""
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return c
    if t == "MultiPolygon":
        return [ring for poly in c for ring in poly]
    if t == "LineString":
        return [c]
    if t == "MultiLineString":
        return c
    raise ValueError(t)


def load(name):
    return json.loads((SRC / f"{name}.json").read_text())["features"]


# ---------------------------------------------------------------------------
# Dissolve the counties into the state outline
# ---------------------------------------------------------------------------
def dissolve(features):
    edges = Counter()
    for f in features:
        for ring in rings_of(f["geometry"]):
            pts = [tuple(p) for p in ring]
            for a, b in zip(pts, pts[1:]):
                edges[tuple(sorted((a, b)))] += 1

    boundary = [e for e, n in edges.items() if n == 1]

    adj = defaultdict(list)
    for a, b in boundary:
        adj[a].append(b)
        adj[b].append(a)

    odd = [v for v, nb in adj.items() if len(nb) != 2]
    if odd:
        raise SystemExit(
            f"county edges do not dissolve cleanly: {len(odd)} node(s) with a "
            "degree other than 2. The source file is not topologically shared "
            "along county borders, so the outline cannot be derived from it."
        )

    rings, seen = [], set()
    for start in adj:
        if start in seen:
            continue
        ring, prev, cur = [start], None, start
        seen.add(start)
        while True:
            nxt = next((n for n in adj[cur] if n != prev), None)
            if nxt is None or nxt == start:
                break
            ring.append(nxt)
            seen.add(nxt)
            prev, cur = cur, nxt
        ring.append(start)
        rings.append(ring)

    rings.sort(key=len, reverse=True)
    return rings


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def main():
    counties = load("counties")
    roads = load("roads")
    rivers = load("rivers")
    lakes = load("lakes")
    places = {f["properties"]["NAME"]: f["geometry"]["coordinates"]
              for f in load("places")}

    try:
        import airportsdata
        airports = airportsdata.load("IATA")
    except ImportError:
        raise SystemExit(
            "airportsdata is not installed.  pip install airportsdata\n"
            "It supplies the airport coordinates (OurAirports data); they are "
            "deliberately not hand-copied into site_data.py."
        )

    # Resolve every facility to a (lon, lat) before projecting, so the extent
    # covers the out-of-state markers too.
    facilities = []
    for f in site_data.FACILITIES:
        f = dict(f)
        if "iata" in f:
            a = airports.get(f["iata"])
            if not a:
                raise SystemExit(f"unknown IATA code {f['iata']} for {f['id']}")
            f["lat"], f["lon"] = a["lat"], a["lon"]
            f.setdefault("precision", "dataset")
            f["source"] = f"OurAirports {f['iata']}"
        elif "place" in f:
            c = places.get(f["place"])
            if not c:
                raise SystemExit(f"unknown place {f['place']} for {f['id']}")
            f["lon"], f["lat"] = c[0], c[1]
            f.setdefault("precision", "dataset")
            f["source"] = "Natural Earth 10m populated places"
        else:
            f.setdefault("precision", "approx")
        facilities.append(f)

    state_rings_ll = dissolve(counties)

    # --- Extent ---------------------------------------------------------
    # Driven by the state outline plus every marker, so nothing falls outside.
    pts = [project(x, y) for ring in state_rings_ll for x, y in ring]
    pts += [project(f["lon"], f["lat"]) for f in facilities]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    scale = (WIDTH - 2 * PAD) / (maxx - minx)
    height = (maxy - miny) * scale + 2 * PAD

    def to_svg(lon, lat):
        x, y = project(lon, lat)
        return ((x - minx) * scale + PAD, (maxy - y) * scale + PAD)

    def conv(geom):
        return [[to_svg(x, y) for x, y in ring] for ring in rings_of(geom)]

    # --- Layers ---------------------------------------------------------
    state_d = path_d([[to_svg(x, y) for x, y in r] for r in state_rings_ll],
                     True, TOL["counties"])

    # Counties carry a label anchor so a highlighted county can name itself.
    # The anchor is the area centroid of the largest ring, which for every
    # Indiana county lies inside it — none is concave enough for the centroid
    # to fall outside.
    county_out = []
    for f in counties:
        rings = conv(f["geometry"])
        county_out.append({
            "id": f["properties"]["COUNTY"],
            "name": f["properties"]["NAME"],
            "d": path_d(rings, True, TOL["counties"]),
            "c": [round(v, 1) for v in centroid(max(rings, key=len))],
        })

    road_out = [{
        "name": f["properties"].get("name"),
        "kind": "beltway" if f["properties"].get("type") == "Beltway" else "interstate",
        "d": path_d(conv(f["geometry"]), False, TOL["roads"]),
    } for f in roads]

    river_out = [{
        "name": f["properties"].get("name"),
        "d": path_d(conv(f["geometry"]), False, TOL["rivers"]),
    } for f in rivers]

    lake_out = [{
        "name": f["properties"].get("name"),
        "d": path_d(conv(f["geometry"]), True, TOL["lakes"]),
    } for f in lakes]

    # Display positions. The separation is deliberately modest — 20 units is
    # about 6.5 km on the ground, which on a map of a 450 km state is well under
    # half a percent and invisible as an error. It moves only the markers that
    # genuinely overlap; everything else stays exactly where it was projected.
    MIN_SEP = 20.0
    true_xy = [to_svg(f["lon"], f["lat"]) for f in facilities]
    shown_xy = declutter(true_xy, MIN_SEP)

    # Each marker's hit area is half the distance to its nearest neighbour, so
    # no two can overlap. An isolated marker gets a generous target; one in a
    # cluster gets a small one, and the chip list under the map is the way in
    # for those.
    # The glyphs are about 11 units in radius, and declutter() has already
    # guaranteed every pair is at least MIN_SEP apart, so d / 2 can never fall
    # below MIN_SEP / 2 — the hit area always covers the mark the visitor sees.
    def hit_radius(i):
        d = min((math.hypot(shown_xy[i][0] - p[0], shown_xy[i][1] - p[1])
                 for j, p in enumerate(shown_xy) if j != i), default=2 * MIN_SEP)
        return round(min(21.0, d / 2.0), 1)

    facility_out = []
    for i, (f, (tx, ty), (x, y)) in enumerate(zip(facilities, true_xy, shown_xy)):
        offset = math.hypot(x - tx, y - ty)
        f = dict(f, displaced=offset > 0.5, hit=hit_radius(i))
        facility_out.append({
            k: v for k, v in {
                "id": f["id"],
                "name": f["name"],
                "short": f.get("short"),
                "sub": f.get("sub"),
                "type": f["type"],
                "x": round(x, 1),
                "y": round(y, 1),
                "lat": round(f["lat"], 5),
                "lon": round(f["lon"], 5),
                "precision": f["precision"],
                "source": f.get("source"),
                "displaced": f.get("displaced", False),
                "hit": f["hit"],
                "network": f.get("network", False),
                "outside": f.get("outside", False),
                "capital": f.get("capital", False),
                "url": f.get("url"),
                "note": f.get("note"),
            }.items() if v is not None and v is not False
        })

    def geo_rings(obj, key):
        return path_d([[to_svg(x, y) for x, y in r] for r in obj[key]],
                      True, TOL["counties"])

    data = {
        "viewBox": [0, 0, round(WIDTH, 1), round(height, 1)],
        "projection": {
            "name": "Albers equal-area conic",
            "lat0": LAT0, "lon0": LON0, "lat1": LAT1, "lat2": LAT2,
        },
        "sources": {
            "boundaries": "US Census Bureau cartographic boundary file, counties, "
                          "1:500,000 (2010). State outline dissolved from them.",
            "roads": "Natural Earth 10m roads",
            "water": "Natural Earth 10m rivers and lakes",
            "cities": "Natural Earth 10m populated places",
            "airports": "OurAirports, via the airportsdata package",
        },
        "state": state_d,
        "counties": county_out,
        "roads": road_out,
        "rivers": river_out,
        "lakes": lake_out,
        "facilities": facility_out,
        "networkCounties": site_data.NETWORK_COUNTIES,
        "ranges": [dict(r, d=geo_rings(r, "rings")) for r in site_data.RANGES],
        "corridors": [dict(c, d=path_d([[to_svg(x, y) for x, y in c["path"]]],
                                       False, 0)) for c in site_data.CORRIDORS],
        "areas": [dict(a, d=geo_rings(a, "rings")) for a in site_data.AREAS],
        "capabilities": [
            {k: v for k, v in c.items() if k != "description"} |
            ({"description": c["description"]} if c.get("description") else {})
            for c in site_data.CAPABILITIES
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "/* GENERATED by tools/build_map.py — do not edit by hand.\n"
        "   Geometry: US Census cartographic boundaries (1:500k), Natural Earth\n"
        "   10m roads/water/places, OurAirports. Projection: Albers equal-area\n"
        "   conic. Edit tools/site_data.py and re-run the script. */\n"
        "window.UAS_MAP = " + json.dumps(data, separators=(",", ":")) + ";\n"
    )

    verts = state_d.count("L") + state_d.count("M")
    print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size // 1024} KB)")
    print(f"  viewBox   {data['viewBox']}")
    print(f"  outline   {verts} vertices in {state_d.count('M')} ring(s)")
    print(f"  counties  {len(county_out)}   roads {len(road_out)}   "
          f"rivers {len(river_out)}   lakes {len(lake_out)}")
    print(f"  markers   {len(facility_out)}  "
          f"({sum(1 for f in facility_out if f.get('network'))} network, "
          f"{sum(1 for f in facility_out if f.get('displaced'))} displaced for legibility)")
    print(f"  verified ranges {len(data['ranges'])}, "
          f"corridors {len(data['corridors'])}, areas {len(data['areas'])}")


if __name__ == "__main__":
    main()
