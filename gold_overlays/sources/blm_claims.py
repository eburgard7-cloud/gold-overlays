"""BLM MLRS mining claims (Not Closed / Closed) via ArcGIS FeatureServer.

NOTE on dates: the public MLRS FeatureServer does NOT expose a true
"located date" or "last action date" field (those live in LR2000 case
files, not this spatial layer). The only date fields present are
`Created`/`Modified`, which are database record timestamps, not legal
claim dates. We use `Created` as a documented proxy for "recorded"
throughout -- see README caveats.
"""
from gold_overlays.config import SOURCES
from gold_overlays.http import arcgis_query_all

ACTIVE_URL = SOURCES["blm_active"]["url"]
CLOSED_URL = SOURCES["blm_closed"]["url"]

FIELDS = "OBJECTID,CSE_NAME,CSE_TYPE_NR,CSE_NR,LEG_CSE_NR,BLM_PROD,CSE_DISP,CSE_META,RCRD_ACRS,Created,Modified"


def _bbox_geometry(bbox):
    minlon, minlat, maxlon, maxlat = bbox
    return f"{minlon},{minlat},{maxlon},{maxlat}"


def _to_claim_dict(feat):
    a = feat["attributes"]
    geom = feat.get("geometry")
    rings = geom.get("rings") if geom else None
    prod = (a.get("BLM_PROD") or "").upper()
    case_type = "placer" if "PLACER" in prod else ("lode" if "LODE" in prod else prod.lower() or "unknown")
    created_ms = a.get("Created")
    created_year = None
    if created_ms:
        import datetime
        created_year = datetime.datetime.utcfromtimestamp(created_ms / 1000).year
    return {
        "name": a.get("CSE_NAME"),
        "serial": a.get("CSE_NR"),
        "legacy_serial": a.get("LEG_CSE_NR"),
        "case_type": case_type,
        "disposition": a.get("CSE_DISP"),
        "acres": a.get("RCRD_ACRS"),
        "quarter_section": a.get("CSE_META"),
        "created_year": created_year,
        "rings": rings,
    }


def fetch_active(bbox, refresh=False):
    geometry = _bbox_geometry(bbox)
    feats = arcgis_query_all(ACTIVE_URL, geometry=geometry, out_fields=FIELDS, refresh=refresh)
    return [_to_claim_dict(f) for f in feats if f.get("geometry")]


def fetch_closed_placer(bbox, refresh=False):
    geometry = _bbox_geometry(bbox)
    where = "UPPER(BLM_PROD) LIKE '%PLACER%'"
    feats = arcgis_query_all(CLOSED_URL, where=where, geometry=geometry, out_fields=FIELDS, refresh=refresh)
    return [_to_claim_dict(f) for f in feats if f.get("geometry")]


def find_by_legacy_serial(serial, refresh=False):
    """Look up a single claim by its legacy ORMC/serial across both active+closed layers."""
    where = f"LEG_CSE_NR='{serial}'"
    for url in (ACTIVE_URL, CLOSED_URL):
        feats = arcgis_query_all(url, where=where, out_fields=FIELDS, refresh=refresh)
        if feats:
            return _to_claim_dict(feats[0]), url
    return None, None
