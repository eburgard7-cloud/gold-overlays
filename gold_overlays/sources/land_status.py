"""BLM Surface Management Agency land status.

The generalized "SMA_Cached_without_PriUnk" service 500s on returnGeometry
for anything but a tiny bbox (its polygons are too complex for the cached
tier). The "SMA_LimitedScale" service exposes one simplified polygon layer
per agency instead, which *does* return geometry -- we use its BLM (id 7)
and USFS (id 9) layers, since those are the only two agencies layer F's
"open ground" filter cares about. The Private/Unknown layer (id 16) 500s
the same way as the cached service and is not queried; anything that is
not BLM and not USFS is reported simply as "non-BLM/USFS" rather than
being split further into State/Private/Other -- see README caveats.
"""
from gold_overlays.config import SOURCES
from gold_overlays.http import cached_get_json

BASE = "https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_LimitedScale/MapServer"
LAYER_IDS = {"BLM": 7, "USFS": 9}


def fetch_land_status(bbox, refresh=False):
    """Returns {"BLM": [rings, ...], "USFS": [rings, ...]} (each a list of
    esri polygon ring-sets, one per returned feature -- usually just one
    multi-part feature per agency).
    """
    minlon, minlat, maxlon, maxlat = bbox
    out = {}
    for agency, layer_id in LAYER_IDS.items():
        params = {
            "geometry": f"{minlon},{minlat},{maxlon},{maxlat}",
            "geometryType": "esriGeometryEnvelope",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "OBJECTID",
            "returnGeometry": "true",
            "outSR": 4326,
            "f": "json",
            "resultRecordCount": 50,
        }
        data = cached_get_json(f"{BASE}/{layer_id}/query", params, refresh=refresh, timeout=120)
        if "error" in data:
            out[agency] = []
            continue
        out[agency] = [f["geometry"]["rings"] for f in data.get("features", []) if f.get("geometry")]
    return out
