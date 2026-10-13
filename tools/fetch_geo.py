#!/usr/bin/env python3
"""
Fetch the public geographic sources the capabilities map is built from, and cut
them down to small Indiana-only extracts in tools/geo-src/.

Why the extracts are committed
------------------------------
The upstream files are 5–50 MB each and live on hosts that may not be reachable
from every build environment. The extracts are a few hundred KB, so they are
committed and `build_map.py` runs offline against them. Re-run this script only
when a source is updated upstream.

    python3 tools/fetch_geo.py          # writes tools/geo-src/*.json

Sources
-------
us-counties-500k   Census Bureau cartographic boundary file, counties, 1:500,000
                   (2010 edition), redistributed as GeoJSON by kjhealy/us-county.
                   The Indiana state outline is DERIVED from these counties by
                   dissolving shared edges, so the outline and the county layer
                   are topologically identical — no slivers where they meet.

ne-roads           Natural Earth 10m roads. Used for the interstate layer.
ne-rivers          Natural Earth 10m river/lake centerlines (Ohio, Wabash, …).
ne-lakes           Natural Earth 10m lakes (Lake Michigan).
ne-places          Natural Earth 10m populated places. Authoritative coordinates
                   for the city markers.

Natural Earth is public domain. Census cartographic boundary files are US
Government works and not subject to copyright.

Airport coordinates do not come from here — build_map.py takes them from the
`airportsdata` package (OurAirports data), which is a better source for them.
"""

import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "geo-src"

NE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"

SOURCES = {
    "us-counties-500k": "https://raw.githubusercontent.com/kjhealy/us-county/master/"
                        "data/geojson/gz_2010_us_050_00_500k.json",
    "ne-roads":  NE + "ne_10m_roads.geojson",
    "ne-rivers": NE + "ne_10m_rivers_lake_centerlines.geojson",
    "ne-lakes":  NE + "ne_10m_lakes.geojson",
    "ne-places": NE + "ne_10m_populated_places.geojson",
}

# Indiana plus enough margin to keep the neighbouring cities and the roads and
# rivers that run up to the state line.
BOX = (-88.8, 37.2, -84.1, 42.4)


def fetch(url, dest):
    print(f"  fetching {url.rsplit('/', 1)[-1]} …", flush=True)
    with urllib.request.urlopen(url, timeout=900) as r:
        dest.write_bytes(r.read())


def coords(geom):
    """Every (lon, lat) pair in a geometry, whatever its nesting depth."""
    depth = {"Point": 0, "LineString": 1, "MultiLineString": 2,
             "Polygon": 2, "MultiPolygon": 3}[geom["type"]]

    def walk(c, d):
        if d == 0:
            yield c
        else:
            for x in c:
                yield from walk(x, d - 1)

    return walk(geom["coordinates"], depth)


def in_box(geom):
    return any(BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3]
               for x, y in coords(geom))


def keep(feature, props):
    """Strip a feature down to the named properties."""
    return {
        "type": "Feature",
        "properties": {k: feature["properties"].get(k) for k in props},
        "geometry": feature["geometry"],
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cache = ROOT / "tools" / ".geo-cache"
    cache.mkdir(exist_ok=True)

    raw = {}
    for name, url in SOURCES.items():
        path = cache / f"{name}.json"
        if not path.exists():
            fetch(url, path)
        # Several of these carry Latin-1 bytes in place names.
        raw[name] = json.loads(path.read_text(encoding="latin-1"))

    # --- Counties -------------------------------------------------------
    counties = [keep(f, ("NAME", "COUNTY"))
                for f in raw["us-counties-500k"]["features"]
                if f["properties"].get("STATE") == "18"]
    counties.sort(key=lambda f: f["properties"]["NAME"])
    write("counties", counties)

    # --- Interstates ----------------------------------------------------
    # "Major Highway" and "Beltway" together are the interstate system; the
    # secondary highways would clutter the map at this size.
    roads = [keep(f, ("name", "type"))
             for f in raw["ne-roads"]["features"]
             if f["properties"].get("type") in ("Major Highway", "Beltway")
             and f["properties"].get("sov_a3") == "USA"
             and in_box(f["geometry"])]
    write("roads", roads)

    # --- Rivers ---------------------------------------------------------
    rivers = [keep(f, ("name",))
              for f in raw["ne-rivers"]["features"] if in_box(f["geometry"])]
    write("rivers", rivers)

    # --- Lakes ----------------------------------------------------------
    lakes = [keep(f, ("name",))
             for f in raw["ne-lakes"]["features"] if in_box(f["geometry"])]
    write("lakes", lakes)

    # --- Populated places -----------------------------------------------
    wanted = {"Indianapolis", "Fort Wayne", "South Bend", "Evansville", "Gary",
              "Terre Haute", "Lafayette", "Bloomington", "Chicago",
              "Cincinnati", "Louisville"}
    places = [keep(f, ("NAME", "ADM1NAME"))
              for f in raw["ne-places"]["features"]
              if f["properties"].get("NAME") in wanted
              and f["properties"].get("ADM0NAME") == "United States of America"
              and in_box(f["geometry"])]
    write("places", places)


def write(name, features):
    path = OUT / f"{name}.json"
    path.write_text(json.dumps(
        {"type": "FeatureCollection", "features": features},
        separators=(",", ":")))
    print(f"wrote {path.relative_to(ROOT)}  ({len(features)} features, "
          f"{path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
