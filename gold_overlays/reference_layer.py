"""'My claims & public sites' layer: verified reference-table points, upgraded
to the real BLM MLRS claim polygon where the public feature service has one.
"""
from shapely.geometry import Point, box as shp_box

from gold_overlays.config import REFERENCE_POINTS
from gold_overlays.http import arcgis_query_all
from gold_overlays.config import SOURCES
from gold_overlays import geo


def _lookup_polygon(serial):
    """Try legacy serial, then SF_ID, across both active+closed layers."""
    fields = "CSE_NAME,CSE_TYPE_NR,CSE_NR,LEG_CSE_NR,BLM_PROD,CSE_DISP,CSE_META,RCRD_ACRS,Created"
    for url in (SOURCES["blm_active"]["url"], SOURCES["blm_closed"]["url"]):
        for where in (f"LEG_CSE_NR='{serial}'", f"SF_ID='{serial}'"):
            feats = arcgis_query_all(url, where=where, out_fields=fields, return_geometry=True)
            if feats and feats[0].get("geometry"):
                a = feats[0]["attributes"]
                prod = (a.get("BLM_PROD") or "").upper()
                case_type = "placer" if "PLACER" in prod else ("lode" if "LODE" in prod else "unknown")
                return {
                    "rings": feats[0]["geometry"]["rings"],
                    "case_name": a.get("CSE_NAME"),
                    "case_type": case_type,
                    "disposition": a.get("CSE_DISP"),
                    "acres": a.get("RCRD_ACRS"),
                    "quarter_section": a.get("CSE_META"),
                }
    return None


def build_reference_features(bbox, refresh=False):
    minlon, minlat, maxlon, maxlat = bbox
    area_box = shp_box(minlon, minlat, maxlon, maxlat)
    features = []
    lookups = []
    for ref in REFERENCE_POINTS:
        pt = Point(ref["lon"], ref["lat"])
        if not area_box.contains(pt):
            continue
        style = "my_claim" if ref["group"] in ("WVM", "BMOA") else "public_site"
        if ref["serial"]:
            poly_info = _lookup_polygon(ref["serial"])
        else:
            poly_info = None
        clipped_rings = None
        if poly_info:
            clipped_rings, _ = geo.clip_rings_to_bbox(
                poly_info["rings"], bbox, prefer_point=(ref["lon"], ref["lat"]),
            )
        if poly_info and clipped_rings:
            desc = (
                f"{ref['group']} | serial {ref['serial']} | {poly_info['case_type']} | "
                f"{poly_info['acres']} ac | {poly_info['disposition']} | "
                f"APPROX (BLM quarter-section) | src: BLM MLRS"
            )
            features.append({
                "type": "polygon",
                "name": f"{ref['name']} [APPROX quarter-section]",
                "description": desc,
                "style": style,
                "coords": clipped_rings,
            })
            lookups.append((ref["name"], "polygon", poly_info["case_name"]))
        else:
            note = "no MLRS polygon available yet" if ref["serial"] else "published site"
            desc = f"{ref['group']} | serial {ref['serial'] or 'n/a'} | precision: {ref['precision']} | {note}"
            features.append({
                "type": "point",
                "name": ref["name"],
                "description": desc,
                "style": style,
                "coords": (ref["lon"], ref["lat"]),
            })
            lookups.append((ref["name"], "point", note))
    return features, lookups
