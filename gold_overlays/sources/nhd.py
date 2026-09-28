"""NHD flowlines, fetched in coarse tiles rather than per-point.

Empirically, this ArcGIS instance takes ~5-8 seconds PER QUERY regardless of
how small the envelope is (server-side cost, not something we control), so a
per-candidate-point query strategy is far too slow once a district has a few
hundred candidates. Instead we bucket candidate points into ~1.6 km tiles,
fetch each tile's flowlines once (with enough padding that a stream just
outside a tile edge is still seen by that tile's query), and let
open_ground.py do all its distance math against the small per-tile result.
"""
import math

from gold_overlays.config import SOURCES
from gold_overlays.http import cached_get_json

NHD_URL = SOURCES["nhd"]["url"]

TILE_M = 1600
PAD_M = 300  # > the 150 m proximity threshold we ultimately test


def tile_key(lon, lat, lat0):
    dlat = TILE_M / 111320.0
    dlon = TILE_M / (111320.0 * max(math.cos(math.radians(lat0)), 0.1))
    return (math.floor(lon / dlon), math.floor(lat / dlat)), dlon, dlat


def tile_bbox(ix, iy, dlon, dlat, pad_deg_lon, pad_deg_lat):
    lon0 = ix * dlon
    lat0 = iy * dlat
    return (lon0 - pad_deg_lon, lat0 - pad_deg_lat, lon0 + dlon + pad_deg_lon, lat0 + dlat + pad_deg_lat)


def fetch_tile(bbox, refresh=False):
    """Returns list of [(lon,lat),...] paths in bbox, or None on error."""
    minlon, minlat, maxlon, maxlat = bbox
    params = {
        "geometry": f"{minlon},{minlat},{maxlon},{maxlat}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "gnis_name",
        "returnGeometry": "true",
        "outSR": 4326,
        "f": "json",
        "resultRecordCount": 2000,
    }
    try:
        data = cached_get_json(NHD_URL + "/query", params, refresh=refresh, timeout=60)
    except Exception:
        return None
    if "error" in data:
        return None
    paths = []
    for feat in data.get("features", []):
        geom = feat.get("geometry")
        if geom and geom.get("paths"):
            for p in geom["paths"]:
                paths.append([(pt[0], pt[1]) for pt in p])
    return paths


def check_service_available(bbox):
    minlon, minlat, maxlon, maxlat = bbox
    cx, cy = (minlon + maxlon) / 2.0, (minlat + maxlat) / 2.0
    dlat = 500 / 111320.0
    dlon = 500 / (111320.0 * max(math.cos(math.radians(cy)), 0.1))
    return fetch_tile((cx - dlon, cy - dlat, cx + dlon, cy + dlat)) is not None
