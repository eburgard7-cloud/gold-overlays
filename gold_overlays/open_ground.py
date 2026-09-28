"""Layer F: derived 'open ground to sample' candidate list.

Rules (per spec):
  1. A/B feature must sit on BLM or USFS surface (land status tag).
  2. Not inside an active-claim polygon. Within 50 m of one is kept but
     flagged "near claim" (claim polygons are only quarter-section accurate).
  3. Within 150 m of a mapped NHD flowline. If NHD is unreachable for this
     area, the filter is skipped and that is recorded in the README.

Ranking: placer > tailings/hydraulic > prospect pit, then by local cluster
density (count of other candidate A/B features within 300 m), then by
distance to the nearest NHD flowline as a tiebreaker.

Deviation from spec: ranking is supposed to break its final tie by
"distance to road". No road dataset was fetched in this build (out of
scope for the time available), so flowline distance is used as the final
tiebreaker instead -- this is called out in the README.

Filters are applied cheapest-first (land status, then claims) so that the
NHD stream check -- which is done with small per-point queries, see
sources/nhd.py -- only has to run for the much smaller surviving set,
not every historical-workings point in the area.
"""
import math

from shapely.geometry import Point, LineString
from shapely.prepared import prep
from shapely.strtree import STRtree

from gold_overlays import geo
from gold_overlays.sources import nhd

TYPE_RANK = {
    "placer": 0,
    "hydraulic": 1,
    "tailings": 1,
    "mine dump": 1,
    "prospect pit": 2,
    "adit": 2,
    "shaft": 2,
}


def _type_rank(ftr_type):
    t = (ftr_type or "").lower()
    for key, rank in TYPE_RANK.items():
        if key in t:
            return rank
    return 3


def build_candidates(usmin_points, milo_mrds_points, land_status_by_agency, active_claim_polygons,
                      nhd_available, area_name, bbox, refresh=False):
    proj = geo.LocalProjector(bbox)

    land_shapes_local = []
    for agency, ring_sets in land_status_by_agency.items():
        for rings in ring_sets:
            poly = geo.esri_rings_to_polygon(rings)
            land_shapes_local.append((prep(proj.to_local(poly)), agency))

    claim_polys_local = [proj.to_local(geo.esri_rings_to_polygon(c["rings"])) for c in active_claim_polygons if c.get("rings")]
    claim_prep_local = [prep(p) for p in claim_polys_local]
    claim_tree = STRtree(claim_polys_local) if claim_polys_local else None

    all_candidates = []
    for p in usmin_points:
        all_candidates.append({
            "lon": p["lon"], "lat": p["lat"],
            "label": f"USMIN {p.get('ftr_type') or 'feature'}",
            "ftr_type": p.get("ftr_type"),
            "source": "USMIN",
        })
    for p in milo_mrds_points:
        ftype = p.get("deposit_class") or p.get("dev_stat") or "prospect"
        all_candidates.append({
            "lon": p["lon"], "lat": p["lat"],
            "label": f"{p.get('site_name') or 'site'} ({ftype})",
            "ftr_type": ftype,
            "source": p.get("_source", "MILO/MRDS"),
        })

    # Pass 1: land status + claim filters (cheap, all in local meters space)
    stage1 = []
    for c in all_candidates:
        local_pt = proj.point_to_local(c["lon"], c["lat"])

        agency = None
        for prepped, ag in land_shapes_local:
            if prepped.contains(local_pt):
                agency = ag
                break
        if agency not in ("BLM", "USFS"):
            continue

        near_claim = False
        inside_claim = False
        if claim_tree is not None:
            for idx in claim_tree.query(local_pt.buffer(50)):
                if claim_prep_local[idx].contains(local_pt):
                    inside_claim = True
                    break
                if local_pt.distance(claim_polys_local[idx]) <= 50:
                    near_claim = True
        if inside_claim:
            continue

        c["agency"] = agency
        c["near_claim"] = near_claim
        c["_local_pt"] = local_pt
        stage1.append(c)

    # Pass 2: NHD stream proximity, fetched in coarse shared tiles (one query
    # per tile, not per point -- this ArcGIS endpoint is ~5-8s/query
    # regardless of envelope size, so per-point queries don't scale).
    results = []
    if nhd_available and stage1:
        lat0 = bbox[1]
        pad_deg_lat = nhd.PAD_M / 111320.0
        pad_deg_lon = nhd.PAD_M / (111320.0 * max(math.cos(math.radians(lat0)), 0.1))

        tiles_needed = {}
        for c in stage1:
            key, dlon, dlat = nhd.tile_key(c["lon"], c["lat"], lat0)
            tiles_needed.setdefault(key, (dlon, dlat))

        tile_results = {}
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=6) as ex:
            futures = {}
            for (ix, iy), (dlon, dlat) in tiles_needed.items():
                bb = nhd.tile_bbox(ix, iy, dlon, dlat, pad_deg_lon, pad_deg_lat)
                futures[ex.submit(nhd.fetch_tile, bb, refresh)] = (ix, iy)
            for fut in as_completed(futures):
                key = futures[fut]
                try:
                    tile_results[key] = fut.result()
                except Exception:
                    tile_results[key] = None

        for c in stage1:
            key, dlon, dlat = nhd.tile_key(c["lon"], c["lat"], lat0)
            paths = tile_results.get(key)
            if paths is None:
                c["dist_to_stream_m"] = None
                results.append(c)
                continue
            if not paths:
                continue
            local_lines = [proj.to_local(LineString(p)) for p in paths if len(p) >= 2]
            if not local_lines:
                continue
            dist_to_stream = min(c["_local_pt"].distance(ln) for ln in local_lines)
            if dist_to_stream > 150:
                continue
            c["dist_to_stream_m"] = dist_to_stream
            results.append(c)
    else:
        for c in stage1:
            c["dist_to_stream_m"] = None
            results.append(c)

    # cluster density: count of other candidates within 300 m (STRtree)
    pts_local = [r["_local_pt"] for r in results]
    pts_tree = STRtree(pts_local) if pts_local else None
    for r in results:
        if pts_tree is None:
            r["cluster_density"] = 0
        else:
            idxs = pts_tree.query(r["_local_pt"].buffer(300))
            r["cluster_density"] = max(0, len(idxs) - 1)
        del r["_local_pt"]

    results.sort(key=lambda c: (
        _type_rank(c["ftr_type"]),
        -c["cluster_density"],
        c["dist_to_stream_m"] if c["dist_to_stream_m"] is not None else 9999,
    ))

    top = results[:25]
    for i, c in enumerate(top, start=1):
        c["waypoint_name"] = f"OPEN-{area_name}-{i:02d}"
    return top, (not nhd_available)
