"""Builds the 6 onX-style layers (style guide section 1) from the raw
per-source fetches in gold_overlays/sources/*. Each build_layerN function
returns (items, report_dict). An "item" is a plain dict:

  {"kind": "wpt", "lon": .., "lat": .., "name": .., "desc": .., "icon": .., "color": ..}
  {"kind": "area", "rings": [[(lon,lat),...], ...], "name": .., "desc": .., "color": .., "style": "solid"/"dot"}
  {"kind": "line", "points": [(lon,lat),...], "name": .., "desc": .., "color": .., "style": "dot"/"dash"}

gold_overlays/render_layers.py turns these into onX GPX / KML / CalTopo GeoJSON.
"""
import math
import re

from shapely.geometry import Point, box as shp_box

from gold_overlays import geo
from gold_overlays.config import REFERENCE_POINTS, SOURCES
from gold_overlays.onx_style import COLOR_YELLOW, COLOR_RED, COLOR_BLACK, ICON_MINERAL_SITE, ICON_LOCATION
from gold_overlays.http import cached_get_json

CLUB_LABELS = {
    "WVM": "Willamette Valley Miners (WVM)",
    "BMOA": "Bohemia Mine Owners Association (BMOA)",
}

MAX_HISTORY = 150
MAX_SCOUT = 10
SCOUT_MERGE_M = 150
HISTORY_MERGE_M = 75


def _clean_claim_name(raw_name):
    name = (raw_name or "").strip()
    name = name.replace("#", "").strip()
    name = re.sub(r"\s+", " ", name)
    return name


# --------------------------------------------------------------- Layer 1 ---
def build_layer1_my_claims(bbox, area_name, refresh=False):
    from gold_overlays.reference_layer import _lookup_polygon

    minlon, minlat, maxlon, maxlat = bbox
    area_box = shp_box(minlon, minlat, maxlon, maxlat)
    items = []
    resolved_serials = set()
    lookups = []
    for ref in REFERENCE_POINTS:
        if ref["group"] not in ("WVM", "BMOA"):
            continue
        pt = Point(ref["lon"], ref["lat"])
        if not area_box.contains(pt):
            continue
        club = CLUB_LABELS[ref["group"]]
        name = _clean_claim_name(ref["name"])
        poly_info = _lookup_polygon(ref["serial"]) if ref["serial"] else None
        clipped_rings = None
        if poly_info:
            clipped_rings, _ = geo.clip_rings_to_bbox(poly_info["rings"], bbox, prefer_point=(ref["lon"], ref["lat"]))
        desc_parts = [f"club: {club}", f"serial: {ref['serial'] or 'n/a'}"]
        if poly_info and clipped_rings:
            desc_parts.append(f"acres: {poly_info['acres']}")
            desc_parts.append("directions: not available (no club handbook source in this build)")
            desc_parts.append("boundary approx (BLM quarter-section)")
            items.append({
                "kind": "area", "rings": clipped_rings, "name": name,
                "desc": " | ".join(desc_parts), "color": COLOR_YELLOW, "style": "solid",
            })
            poly = geo.esri_rings_to_polygon(clipped_rings)
            c = poly.centroid
            items.append({
                "kind": "wpt", "lon": c.x, "lat": c.y, "name": name,
                "desc": " | ".join(desc_parts), "icon": ICON_MINERAL_SITE, "color": COLOR_YELLOW,
            })
            resolved_serials.add(ref["serial"])
            lookups.append((name, "area+pin", poly_info["case_name"]))
        else:
            desc_parts.append("acres: n/a")
            desc_parts.append("directions: not available (no club handbook source in this build)")
            desc_parts.append("no BLM MLRS polygon available yet -- point only, not an invented boundary")
            items.append({
                "kind": "wpt", "lon": ref["lon"], "lat": ref["lat"], "name": name,
                "desc": " | ".join(desc_parts), "icon": ICON_MINERAL_SITE, "color": COLOR_YELLOW,
            })
            lookups.append((name, "pin-only", "no MLRS polygon"))
    report = {"count": len(items), "lookups": lookups}
    return items, resolved_serials, report


# --------------------------------------------------------------- Layer 2 ---
def build_layer2_public(bbox, area_name):
    minlon, minlat, maxlon, maxlat = bbox
    area_box = shp_box(minlon, minlat, maxlon, maxlat)
    items = []
    for ref in REFERENCE_POINTS:
        if ref["group"] != "public":
            continue
        pt = Point(ref["lon"], ref["lat"])
        if not area_box.contains(pt):
            continue
        name = _clean_claim_name(ref["name"])
        desc = f"public panning site | precision: {ref['precision']} | status: unconfirmed-green, using black (no confirmed onX green)"
        items.append({
            "kind": "wpt", "lon": ref["lon"], "lat": ref["lat"], "name": name,
            "desc": desc, "icon": ICON_LOCATION, "color": COLOR_BLACK,
        })
    report = {
        "count": len(items),
        "corridor_areas_skipped": (
            "no verified public-corridor extent geometry source in this build -- "
            "not rendered rather than invented"
        ),
    }
    return items, report


# --------------------------------------------------------------- Layer 3 ---
def build_layer3_other_claims(active_claims_raw, exclude_serials, bbox):
    items = []
    n_clipped = 0
    n_excluded = 0
    for c in active_claims_raw:
        if not c["rings"]:
            continue
        if c.get("serial") in exclude_serials or c.get("legacy_serial") in exclude_serials:
            n_excluded += 1
            continue
        clipped_rings, was_clipped = geo.clip_rings_to_bbox(c["rings"], bbox)
        if clipped_rings is None:
            continue
        if was_clipped:
            n_clipped += 1
        name = _clean_claim_name(c["name"])
        desc = (
            f"{c['case_type']} | serial {c['legacy_serial'] or c['serial']} | {c['acres']} ac | "
            f"{c['disposition']} | qtr-sec {c['quarter_section']} | recorded~{c['created_year']} "
            "(DB date, not legal located date) | src: BLM MLRS Not Closed | "
            "boundary approx (BLM quarter-section) | do not dig here (active claim)"
        )
        items.append({
            "kind": "area", "rings": clipped_rings, "name": name, "desc": desc,
            "color": COLOR_RED, "style": "dot",
        })
    report = {"count": len(items), "clipped_to_bbox": n_clipped, "excluded_as_my_claims": n_excluded}
    return items, report


# --------------------------------------------------------------- Layer 4 ---
_USMIN_PLACER_TAILINGS_HYDRAULIC = {
    "placer": "Placer", "placer mine": "Placer",
    "tailings": "Tailings",
    "hydraulic": "Hydraulic", "hydraulic mine": "Hydraulic",
}
_USMIN_ADIT_SHAFT = {
    "adit": "Adit", "adit/tunnel": "Adit", "tunnel": "Adit",
    "shaft": "Shaft", "mine shaft": "Shaft",
}
USMIN_SURFACE_WORKING_TYPES = {
    "placer", "placer mine", "hydraulic", "hydraulic mine", "tailings",
    "mine dump", "dump", "prospect pit", "trench", "pit", "open pit mine",
}


def _usmin_subtype(ftr_type):
    t = (ftr_type or "").strip().lower()
    if t in _USMIN_PLACER_TAILINGS_HYDRAULIC:
        return _USMIN_PLACER_TAILINGS_HYDRAULIC[t], ICON_MINERAL_SITE
    if t in _USMIN_ADIT_SHAFT:
        return _USMIN_ADIT_SHAFT[t], ICON_LOCATION
    if "pit" in t:
        return "Pit", ICON_LOCATION
    if "dump" in t:
        return "Dump", ICON_LOCATION
    return "Site", ICON_LOCATION


def _milo_subtype(deposit_class, site_name):
    dc = (deposit_class or "").lower()
    if "placer" in dc:
        return "Placer", ICON_MINERAL_SITE
    return "Mine", ICON_LOCATION


def _is_generic_name(name):
    n = (name or "").strip().lower()
    return n in ("", "unnamed", "unknown", "n/a")


class _Cluster:
    __slots__ = ("lon", "lat", "n", "members")

    def __init__(self, lon, lat, member):
        self.lon = lon
        self.lat = lat
        self.n = 1
        self.members = [member]

    def add(self, lon, lat, member):
        self.lon = (self.lon * self.n + lon) / (self.n + 1)
        self.lat = (self.lat * self.n + lat) / (self.n + 1)
        self.n += 1
        self.members.append(member)


def _greedy_cluster(records, radius_m):
    """records: list of dict with lon/lat. Leader/centroid clustering: assign
    each record to the nearest existing cluster centroid if within radius_m,
    else start a new cluster. Bounds cluster diameter far better than
    single-linkage chaining on dense point fields.
    """
    clusters = []
    for r in records:
        best = None
        best_d = None
        for cl in clusters:
            d = geo.point_distance_m(r["lon"], r["lat"], cl.lon, cl.lat)
            if d <= radius_m and (best_d is None or d < best_d):
                best, best_d = cl, d
        if best is not None:
            best.add(r["lon"], r["lat"], r)
        else:
            clusters.append(_Cluster(r["lon"], r["lat"], r))
    return clusters


def build_layer4_history(usmin_pts, usmin_polys, milo_sites, mrds_kept, bbox):
    records = []
    for p in usmin_pts:
        prefix, icon = _usmin_subtype(p.get("ftr_type"))
        records.append({
            "lon": p["lon"], "lat": p["lat"], "prefix": prefix, "icon": icon,
            "name": p.get("topo_name"), "informative_name": bool(p.get("topo_name")),
            "source": "USMIN", "is_pit": prefix == "Pit",
        })
    for p in usmin_polys:
        poly = geo.esri_rings_to_polygon(p["rings"])
        if poly.is_empty:
            continue
        c = poly.centroid
        prefix, icon = _usmin_subtype(p.get("ftr_type"))
        records.append({
            "lon": c.x, "lat": c.y, "prefix": prefix, "icon": icon,
            "name": p.get("topo_name"), "informative_name": bool(p.get("topo_name")),
            "source": "USMIN", "is_pit": prefix == "Pit",
        })

    usmin_only_pts = [(p["lon"], p["lat"]) for p in usmin_pts] + [
        (geo.esri_rings_to_polygon(p["rings"]).centroid.x, geo.esri_rings_to_polygon(p["rings"]).centroid.y)
        for p in usmin_polys if not geo.esri_rings_to_polygon(p["rings"]).is_empty
    ]

    dropped_generic_milo = 0
    for s in milo_sites:
        if _is_generic_name(s["site_name"]) and (s.get("deposit_class") or "").lower() == "unknown":
            near_usmin = any(
                geo.point_distance_m(s["lon"], s["lat"], ux, uy) <= 100 for ux, uy in usmin_only_pts
            )
            if not near_usmin:
                dropped_generic_milo += 1
                continue
        prefix, icon = _milo_subtype(s.get("deposit_class"), s.get("site_name"))
        records.append({
            "lon": s["lon"], "lat": s["lat"], "prefix": prefix, "icon": icon,
            "name": s.get("site_name"), "informative_name": not _is_generic_name(s.get("site_name")),
            "source": "MILO", "is_pit": False,
        })
    for m in mrds_kept:
        prefix, icon = _milo_subtype(m.get("deposit_class") or m.get("dev_stat"), m.get("site_name"))
        records.append({
            "lon": m["lon"], "lat": m["lat"], "prefix": prefix, "icon": icon,
            "name": m.get("site_name"), "informative_name": not _is_generic_name(m.get("site_name")),
            "source": "MRDS", "is_pit": False,
        })

    clusters = _greedy_cluster(records, HISTORY_MERGE_M)

    scored = []
    for cl in clusters:
        priority_order = {"Placer": 0, "Tailings": 0, "Hydraulic": 0, "Adit": 1, "Shaft": 1}
        best = min(cl.members, key=lambda m: (priority_order.get(m["prefix"], 2), not m["informative_name"]))
        informative = sorted(
            (m for m in cl.members if m["informative_name"]),
            key=lambda m: priority_order.get(m["prefix"], 2),
        )
        site_label = informative[0]["name"] if informative else None
        sources = sorted({m["source"] for m in cl.members})
        desc = f"{cl.n} source record(s) merged within {HISTORY_MERGE_M}m | src: {', '.join(sources)}"
        name = f"{best['prefix']} - {site_label}" if site_label else f"{best['prefix']} (unnamed)"
        scored.append({
            "kind": "wpt", "lon": cl.lon, "lat": cl.lat, "name": name, "desc": desc,
            "icon": best["icon"], "color": COLOR_BLACK,
            "_is_pit": all(m["is_pit"] for m in cl.members), "_n": cl.n,
            "_priority": priority_order.get(best["prefix"], 2),
        })

    non_pit = [s for s in scored if not s["_is_pit"]]
    pit = [s for s in scored if s["_is_pit"]]
    pit.sort(key=lambda s: -s["_n"])
    dropped_pits_for_cap = 0
    budget = MAX_HISTORY - len(non_pit)
    if budget < 0:
        non_pit.sort(key=lambda s: (s["_priority"], -s["_n"]))
        dropped_pits_for_cap += len(pit)
        pit = []
        non_pit = non_pit[:MAX_HISTORY]
    else:
        if len(pit) > budget:
            dropped_pits_for_cap = len(pit) - budget
            pit = pit[:budget]

    final = non_pit + pit
    for item in final:
        del item["_is_pit"], item["_n"], item["_priority"]

    report = {
        "raw_records": len(records),
        "clusters_before_cap": len(scored),
        "dropped_generic_milo_far_from_usmin": dropped_generic_milo,
        "dropped_prospect_pits_over_cap": dropped_pits_for_cap,
        "final_count": len(final),
        "max_allowed": MAX_HISTORY,
    }
    return final, report


# --------------------------------------------------------------- Layer 5 ---
_SMA_PRIUNK_URL = "https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_Cached_with_PriUnk/MapServer"
_SMA_LAYER_IDS = {"BLM": 22, "USFS": 24, "OTHER_FED": 28, "STATE": 29, "LOCAL": 30, "PRIVATE_UNKNOWN": 31}


def _point_land_check(lon, lat):
    """Point-level re-check against the (non-generalized-bbox) BLM SMA
    'Cached_with_PriUnk' FEATURES sublayers. Small point queries avoid the
    500/502 the 'Cached' tier throws on returnGeometry=true over a large
    bbox (see gold_overlays/sources/land_status.py). Returns
    ("public"/"private"/"unverifiable", agency_or_None).
    """
    for agency, layer_id in (("BLM", 22), ("USFS", 24)):
        try:
            data = cached_get_json(
                f"{_SMA_PRIUNK_URL}/{layer_id}/query",
                {
                    "geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint", "inSR": 4326,
                    "spatialRel": "esriSpatialRelIntersects", "outFields": "OBJECTID",
                    "returnGeometry": "false", "f": "json",
                },
                timeout=20,
            )
            if data.get("features"):
                return "public", agency
        except Exception:
            continue
    try:
        data = cached_get_json(
            f"{_SMA_PRIUNK_URL}/31/query",
            {
                "geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint", "inSR": 4326,
                "spatialRel": "esriSpatialRelIntersects", "outFields": "OBJECTID",
                "returnGeometry": "false", "f": "json",
            },
            timeout=20,
        )
        if data.get("features"):
            return "private", None
        return "public", None
    except Exception:
        return "unverifiable", None


def _is_placer_labeled(candidate, usmin_pts, mrds_pts):
    ftype = (candidate.get("ftr_type") or "").lower()
    if "placer" in ftype:
        return True
    # proximity: within 50m of a USMIN surface working or an MRDS placer record
    for p in usmin_pts:
        if (p.get("ftr_type") or "").strip().lower() in USMIN_SURFACE_WORKING_TYPES:
            if geo.point_distance_m(candidate["lon"], candidate["lat"], p["lon"], p["lat"]) <= 50:
                return True
    for m in mrds_pts:
        if "placer" in (m.get("dev_stat") or "").lower() or "placer" in (m.get("site_name") or "").lower():
            if geo.point_distance_m(candidate["lon"], candidate["lat"], m["lon"], m["lat"]) <= 50:
                return True
    return False


def build_layer5_scout(usmin_pts, milo_mrds_points, mrds_pts, land_by_agency, active_claim_polygons,
                        nhd_available, area_name, bbox, refresh=False):
    from gold_overlays import open_ground

    candidates, nhd_skipped = open_ground.build_candidates(
        usmin_pts, milo_mrds_points, land_by_agency, active_claim_polygons, nhd_available, area_name, bbox,
        refresh=refresh,
    )
    # open_ground already ranks/sorts; re-derive a larger pool (it caps at 25
    # internally) by re-reading its module-level TYPE_RANK ordering -- we
    # only get its top-25 back, which is plenty of pool for our top-10.
    selected = []
    land_checks = {"public_confirmed": 0, "private_dropped": 0, "unverifiable": 0}
    for c in candidates:
        if len(selected) >= MAX_SCOUT:
            break
        if any(geo.point_distance_m(c["lon"], c["lat"], s["lon"], s["lat"]) < SCOUT_MERGE_M for s in selected):
            continue
        status, agency = _point_land_check(c["lon"], c["lat"])
        if status == "private":
            land_checks["private_dropped"] += 1
            continue
        elif status == "unverifiable":
            land_checks["unverifiable"] += 1
        else:
            land_checks["public_confirmed"] += 1
        c["_land_status"] = status
        selected.append(c)

    items = []
    for i, c in enumerate(selected, start=1):
        placer = _is_placer_labeled(c, usmin_pts, mrds_pts)
        label = "Placer bench" if placer else "Lode/unknown outcrop"
        name = f"SCOUT {i} - {label}"
        stream_txt = f"{c['dist_to_stream_m']:.0f}m to stream" if c.get("dist_to_stream_m") is not None else "stream dist n/a"
        near = " | NEAR ACTIVE CLAIM (<50m, approx)" if c["near_claim"] else ""
        check_owner = " | (check owner)" if c.get("_land_status") == "unverifiable" else ""
        desc = (
            f"{c['label']} | agency: {c['agency']} | {stream_txt} | cluster: {c['cluster_density']} nearby{near} | "
            f"src: {c['source']}{check_owner}"
        )
        items.append({
            "kind": "wpt", "lon": c["lon"], "lat": c["lat"], "name": name, "desc": desc,
            "icon": ICON_LOCATION, "color": COLOR_RED,
        })

    # assert pairwise spacing (construction-time invariant, not just a filter)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            d = geo.point_distance_m(items[i]["lon"], items[i]["lat"], items[j]["lon"], items[j]["lat"])
            assert d >= SCOUT_MERGE_M, f"scout candidates {i},{j} only {d:.0f}m apart"

    report = {
        "count": len(items), "nhd_skipped": nhd_skipped, "candidate_pool": len(candidates),
        "land_checks": land_checks,
    }
    return items, report


# --------------------------------------------------------------- Layer 6 ---
def _norm_name(s):
    return "".join(ch for ch in (s or "").lower() if ch.isalnum())


def dedup_mrds_against_milo(milo_sites, mrds_sites):
    from collections import defaultdict
    milo_by_name = defaultdict(list)
    for s in milo_sites:
        milo_by_name[_norm_name(s["site_name"])].append(s)
    kept = []
    for m in mrds_sites:
        dup = any(
            geo.point_distance_m(m["lon"], m["lat"], s["lon"], s["lat"]) <= 250
            for s in milo_by_name.get(_norm_name(m["site_name"]), [])
        )
        if not dup:
            m2 = dict(m)
            m2["deposit_class"] = m.get("dev_stat")
            kept.append(m2)
    return kept


def build_layer6_access(area_name):
    items = []
    report = {
        "count": 0,
        "reason": (
            "no club handbook / access-directions source data exists in this repo -- "
            "skipped rather than inventing a route"
        ),
    }
    return items, report
