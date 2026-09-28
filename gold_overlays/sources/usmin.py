from gold_overlays.config import USMIN_KEEP_TYPES, USMIN_DROP_TYPES, SOURCES
from gold_overlays.ogr_retry import run_ogr2ogr

WFS_BASE = SOURCES["usmin"]["wfs_base"]


def fetch_points(bbox, refresh=False):
    """Fetch USMIN point features (mine/prospect features) in bbox via WFS+ogr2ogr, filtered to keep-list."""
    import subprocess
    import json
    import os
    import hashlib

    minlon, minlat, maxlon, maxlat = bbox
    cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "cache")
    cache_dir = os.path.abspath(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)
    key = hashlib.sha256(f"usmin_points_{bbox}".encode()).hexdigest()
    out_path = os.path.join(cache_dir, key + ".geojson")
    if refresh or not os.path.exists(out_path):
        run_ogr2ogr([
            "ogr2ogr", "-f", "GeoJSON", "-overwrite", out_path,
            f"WFS:{WFS_BASE}", "ms:points",
            "-spat", str(minlon), str(minlat), str(maxlon), str(maxlat),
        ])
    with open(out_path) as f:
        data = json.load(f)

    kept = []
    dropped_types = set()
    for feat in data.get("features", []):
        props = feat["properties"]
        ftr_type = (props.get("ftr_type") or "").strip().lower()
        if ftr_type in USMIN_DROP_TYPES:
            dropped_types.add(ftr_type)
            continue
        if USMIN_KEEP_TYPES and ftr_type not in USMIN_KEEP_TYPES:
            # Unknown type: keep it (better to surface than silently drop),
            # but tag so the description makes that clear.
            props["_unmapped_type"] = True
        coords = feat["geometry"]["coordinates"]
        kept.append({
            "lon": coords[0], "lat": coords[1],
            "ftr_type": props.get("ftr_type"),
            "topo_name": props.get("topo_name"),
            "topo_date": props.get("topo_date"),
            "topo_scale": props.get("topo_scale"),
            "url": props.get("url"),
        })
    return kept, dropped_types


def fetch_polygons(bbox, refresh=False):
    import subprocess
    import json
    import os
    import hashlib

    minlon, minlat, maxlon, maxlat = bbox
    cache_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "cache"))
    os.makedirs(cache_dir, exist_ok=True)
    key = hashlib.sha256(f"usmin_polygons_{bbox}".encode()).hexdigest()
    out_path = os.path.join(cache_dir, key + ".geojson")
    if refresh or not os.path.exists(out_path):
        run_ogr2ogr([
            "ogr2ogr", "-f", "GeoJSON", "-overwrite", out_path,
            f"WFS:{WFS_BASE}", "ms:polygons",
            "-spat", str(minlon), str(minlat), str(maxlon), str(maxlat),
        ])
    with open(out_path) as f:
        data = json.load(f)

    kept = []
    dropped_types = set()
    for feat in data.get("features", []):
        props = feat["properties"]
        ftr_type = (props.get("ftr_type") or "").strip().lower()
        if ftr_type in USMIN_DROP_TYPES:
            dropped_types.add(ftr_type)
            continue
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            rings = [geom["coordinates"][0]] + list(geom["coordinates"][1:])
        else:
            rings = geom["coordinates"][0]
        kept.append({
            "rings": rings,
            "ftr_type": props.get("ftr_type"),
            "topo_name": props.get("topo_name"),
            "topo_date": props.get("topo_date"),
            "topo_scale": props.get("topo_scale"),
            "url": props.get("url"),
        })
    return kept, dropped_types
