"""Layer G (lidar hillshade GeoTIFF+GeoPDF) and Layer H (historical topo
GeoPDF) downloads. Kept separate from build.py's KML/GPX path since these
are slow, large, binary outputs -- run via `python build.py --rasters`.
"""
import json
import os
import re

from gold_overlays.config import REFERENCE_POINTS, AREAS, SOURCES
from gold_overlays.sources import lidar, topo

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")

# Areas that actually contain a club claim from the reference table (used to
# decide which areas get historical-topo downloads, capped at ~10 files total).
CLAIM_CLUSTER_AREAS = ["bohemia", "quartzville", "calapooia", "lnf_santiam", "cowcreek"]
MAX_TOPO_FILES = 10
MAX_TOPO_BYTES = 150 * 1024 * 1024


def _slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _points_for_area(bbox):
    from shapely.geometry import Point, box as shp_box
    area_box = shp_box(*bbox)
    seen = {}
    for ref in REFERENCE_POINTS:
        pt = Point(ref["lon"], ref["lat"])
        if not area_box.contains(pt):
            continue
        key = (round(ref["lon"], 4), round(ref["lat"], 4))
        if key in seen:
            seen[key]["names"].append(ref["name"])
            continue
        seen[key] = {"lon": ref["lon"], "lat": ref["lat"], "names": [ref["name"]]}
    return list(seen.values())


def build_lidar_for_area(area_name, refresh=False):
    bbox = AREAS[area_name]
    points = _points_for_area(bbox)
    out_dir = os.path.join(OUT_DIR, area_name, "lidar")
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for p in points:
        slug = _slug(p["names"][0])
        tif_path = os.path.join(out_dir, f"{slug}.tif")
        pdf_path = os.path.join(out_dir, f"{slug}.pdf")
        if os.path.exists(tif_path) and not refresh:
            ok = True
        else:
            print(f"    lidar export: {p['names'][0]} ({p['lat']:.4f},{p['lon']:.4f})", flush=True)
            ok = lidar.export_hillshade_tif(p["lon"], p["lat"], tif_path)
        if not ok:
            results.append({"names": p["names"], "status": "export_failed", "viewer": SOURCES["lidar"]["viewer"]})
            continue
        pdf_ok = lidar.make_geopdf(tif_path, None, pdf_path, layer_name=slug)
        results.append({
            "names": p["names"], "status": "ok",
            "tif": tif_path, "pdf": pdf_path if pdf_ok else None,
            "tif_bytes": os.path.getsize(tif_path),
        })
    with open(os.path.join(out_dir, "lidar_report.json"), "w") as f:
        json.dump(results, f, indent=2)
    return results


_topo_files_downloaded = 0


def build_topo_for_area(area_name, refresh=False):
    global _topo_files_downloaded
    bbox = AREAS[area_name]
    out_dir = os.path.join(OUT_DIR, area_name, "topo")
    os.makedirs(out_dir, exist_ok=True)
    items = topo.list_historical_topos(bbox, refresh=refresh)
    picks = []
    for scale_kw in ("15 x 15", "7.5 x 7.5"):
        item = topo.pick_oldest(items, scale_kw)
        if item:
            picks.append((scale_kw, item))

    results = []
    for scale_kw, item in picks:
        if _topo_files_downloaded >= MAX_TOPO_FILES:
            results.append({"scale": scale_kw, "title": item["title"], "status": "skipped (global 10-file cap reached)"})
            continue
        fname = re.sub(r"[^A-Za-z0-9]+", "_", item["title"]) + ".pdf"
        dest = os.path.join(out_dir, fname)
        if os.path.exists(dest) and not refresh:
            results.append({"scale": scale_kw, "title": item["title"], "status": "cached", "path": dest})
            continue
        ok, reason = topo.download(item, dest, max_bytes=MAX_TOPO_BYTES, refresh=refresh)
        if ok:
            _topo_files_downloaded += 1
            results.append({"scale": scale_kw, "title": item["title"], "status": "downloaded", "path": dest,
                             "bytes": os.path.getsize(dest)})
        else:
            results.append({"scale": scale_kw, "title": item["title"], "status": f"skipped ({reason})"})
    with open(os.path.join(out_dir, "topo_report.json"), "w") as f:
        json.dump(results, f, indent=2)
    return results
