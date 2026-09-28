"""DOGAMI MILO-4 gold/silver mine & prospect sites (file geodatabase)."""
import json
import os
import subprocess
import zipfile

from gold_overlays.config import SOURCES
from gold_overlays.http import cached_download

_CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "cache"))
_GDB_DIR = os.path.join(_CACHE_DIR, "MILO4_GIS_bundle")
_GDB_PATH = os.path.join(_GDB_DIR, "MILOv4.gdb")


def _ensure_gdb(refresh=False):
    zip_path = os.path.join(_CACHE_DIR, "milo4_gis_bundle.zip")
    if refresh or not os.path.exists(_GDB_PATH):
        cached_download(SOURCES["milo4"]["gis_bundle"], zip_path, refresh=refresh)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(_CACHE_DIR)
    return _GDB_PATH


def _classify_deposit(deposit_type, workings_type):
    dt = (deposit_type or "").lower()
    wt = (workings_type or "").lower()
    if "placer" in dt:
        return "placer"
    if any(k in dt for k in ("vein", "shear", "lode", "disseminated")):
        return "lode"
    if wt == "underground":
        return "lode"
    if wt == "surface":
        return "placer (heuristic: surface workings)"
    return "unknown"


def fetch_gold_sites(bbox, refresh=False):
    gdb = _ensure_gdb(refresh=refresh)
    minlon, minlat, maxlon, maxlat = bbox
    import hashlib
    key = hashlib.sha256(f"milo_{bbox}".encode()).hexdigest()
    out_path = os.path.join(_CACHE_DIR, key + "_milo.geojson")
    if refresh or not os.path.exists(out_path):
        subprocess.run(
            [
                "ogr2ogr", "-f", "GeoJSON", "-overwrite", "-t_srs", "EPSG:4326", out_path,
                gdb, "MILO",
                "-spat", str(minlon), str(minlat), str(maxlon), str(maxlat),
                "-spat_srs", "EPSG:4326",
            ],
            check=True, capture_output=True,
        )
    with open(out_path) as f:
        data = json.load(f)

    sites = []
    for feat in data.get("features", []):
        p = feat["properties"]
        commodity = p.get("Commodity") or ""
        if "gold" not in commodity.lower():
            continue
        lon, lat = feat["geometry"]["coordinates"]
        sites.append({
            "lon": lon, "lat": lat,
            "site_name": p.get("SiteName") or p.get("Synonym") or "unnamed",
            "commodity": commodity,
            "deposit_type": p.get("DepositType"),
            "workings_type": p.get("WorkingsType"),
            "deposit_class": _classify_deposit(p.get("DepositType"), p.get("WorkingsType")),
            "development_status": p.get("WorkingsDescription"),
            "product_size": p.get("ProductSize"),
            "commodities_produced": p.get("CommoditiesProduced"),
            "year_discovery": p.get("YearOfDiscovery"),
            "year_production": p.get("YearProductionStarted"),
            "milo_id": p.get("MILO_ID"),
        })
    return sites
