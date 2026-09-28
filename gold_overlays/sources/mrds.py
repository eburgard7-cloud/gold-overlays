"""USGS MRDS via WFS (mrdata.usgs.gov). Only a limited attribute set is
exposed by the public WFS (dep_id, site_name, dev_stat, code_list, url) --
full commodity/deposit-type/production detail lives on the per-site HTML
page linked by `url` and is not scraped here to keep the pipeline fast.
"""
import hashlib
import json
import os

from gold_overlays.config import SOURCES
from gold_overlays.ogr_retry import run_ogr2ogr

WFS_BASE = SOURCES["mrds"]["wfs_base"]
_CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "cache"))


def fetch_gold_sites(bbox, refresh=False):
    minlon, minlat, maxlon, maxlat = bbox
    os.makedirs(_CACHE_DIR, exist_ok=True)
    key = hashlib.sha256(f"mrds_{bbox}".encode()).hexdigest()
    out_path = os.path.join(_CACHE_DIR, key + ".geojson")
    if refresh or not os.path.exists(out_path):
        run_ogr2ogr([
            "ogr2ogr", "-f", "GeoJSON", "-overwrite", out_path,
            f"WFS:{WFS_BASE}", "ms:mrds",
            "-spat", str(minlon), str(minlat), str(maxlon), str(maxlat),
        ])
    with open(out_path) as f:
        data = json.load(f)

    gold = []
    for feat in data.get("features", []):
        props = feat["properties"]
        codes = (props.get("code_list") or "").upper()
        if "AU" not in codes.split(","):
            continue
        coords = feat["geometry"]["coordinates"]
        gold.append({
            "lon": coords[0], "lat": coords[1],
            "site_name": props.get("site_name"),
            "dev_stat": props.get("dev_stat"),
            "code_list": props.get("code_list"),
            "url": props.get("url"),
            "dep_id": props.get("dep_id"),
        })
    return gold
