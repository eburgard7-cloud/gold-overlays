#!/usr/bin/env python3
"""Build onX-ready KML/GPX gold-prospecting overlays for one or all areas.

Usage:
    python build.py --area bohemia
    python build.py --area all
    python build.py --area all --refresh      # bypass the on-disk cache
    python build.py --check-bboxes            # NHD creek-coverage sanity check only
"""
import argparse
import datetime
import json
import math
import os
import sys
from collections import Counter, defaultdict

from shapely.geometry import Point, shape as shp_shape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gold_overlays.config import AREAS, AREA_LABELS, SOURCES, REFERENCE_POINTS
from gold_overlays import geo, render, reference_layer, open_ground
from gold_overlays.sources import usmin, mrds, milo, blm_claims, land_status, nhd, lidar, topo
from gold_overlays.area_readme import write_area_readme
try:
    from gold_overlays.bulletin_notes import NOTES as BULLETIN_NOTES
except ImportError:
    BULLETIN_NOTES = {}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
TODAY = datetime.date.today().isoformat()


def clip300(s):
    s = s or ""
    return s if len(s) <= 300 else s[:299] + "…"


# ---------------------------------------------------------------- USMIN ----
def build_usmin_features(bbox, refresh):
    pts, dropped_pt_types = usmin.fetch_points(bbox, refresh)
    polys, dropped_poly_types = usmin.fetch_polygons(bbox, refresh)
    features = []
    for p in pts:
        desc = clip300(f"USMIN {p['ftr_type']} | topo: {p['topo_name']} ({p['topo_date']}) 1:{p['topo_scale']} | src: USGS USMIN")
        features.append({
            "type": "point", "name": p["ftr_type"] or "USMIN feature",
            "description": desc, "style": "usmin", "coords": (p["lon"], p["lat"]),
        })
    for p in polys:
        clipped_rings, _ = geo.clip_rings_to_bbox(p["rings"], bbox)
        if clipped_rings is None:
            continue
        desc = clip300(f"USMIN {p['ftr_type']} | topo: {p['topo_name']} ({p['topo_date']}) 1:{p['topo_scale']} | src: USGS USMIN")
        features.append({
            "type": "polygon", "name": p["ftr_type"] or "USMIN feature",
            "description": desc, "style": "usmin_polygon", "coords": clipped_rings,
        })
    dropped = dropped_pt_types | dropped_poly_types
    return features, pts, polys, dropped


# ------------------------------------------------------------ MILO/MRDS ----
def _norm_name(s):
    return "".join(ch for ch in (s or "").lower() if ch.isalnum())


def build_milo_mrds_features(bbox, refresh):
    milo_sites = milo.fetch_gold_sites(bbox, refresh)
    mrds_sites = mrds.fetch_gold_sites(bbox, refresh)

    milo_by_name = defaultdict(list)
    for s in milo_sites:
        milo_by_name[_norm_name(s["site_name"])].append(s)

    kept_mrds = []
    for m in mrds_sites:
        dup = False
        for s in milo_by_name.get(_norm_name(m["site_name"]), []):
            if geo.point_distance_m(m["lon"], m["lat"], s["lon"], s["lat"]) <= 250:
                dup = True
                break
        if not dup:
            kept_mrds.append(m)

    features = []
    combined_points = []
    for s in milo_sites:
        desc = clip300(
            f"MILO gold | {s['commodity']} | {s['deposit_class']} | "
            f"discovered {s['year_discovery'] or '?'} | prod started {s['year_production'] or '?'} | "
            f"size: {s['product_size'] or 'n/a'} | src: DOGAMI MILO-4 {s['milo_id'] or ''}"
        )
        features.append({
            "type": "point", "name": s["site_name"], "description": desc,
            "style": "milo_gold", "coords": (s["lon"], s["lat"]),
        })
        s2 = dict(s)
        s2["_source"] = "MILO"
        combined_points.append(s2)
    for m in kept_mrds:
        desc = clip300(f"MRDS gold occurrence | status: {m['dev_stat']} | commodities: {m['code_list']} | src: {m['url']}")
        features.append({
            "type": "point", "name": m["site_name"] or "MRDS site", "description": desc,
            "style": "site_other", "coords": (m["lon"], m["lat"]),
        })
        m2 = dict(m)
        m2["_source"] = "MRDS"
        m2["deposit_class"] = m.get("dev_stat")
        combined_points.append(m2)
    return features, combined_points, len(milo_sites), len(mrds_sites), len(kept_mrds)


# ------------------------------------------------------------- Claims C ----
def build_active_claims_features(bbox, refresh):
    claims = blm_claims.fetch_active(bbox, refresh)
    features = []
    n_clipped = 0
    for c in claims:
        if not c["rings"]:
            continue
        clipped_rings, was_clipped = geo.clip_rings_to_bbox(c["rings"], bbox)
        if clipped_rings is None:
            continue
        if was_clipped:
            n_clipped += 1
        desc = clip300(
            f"{c['case_type']} | serial {c['legacy_serial'] or c['serial']} | {c['acres']} ac | "
            f"{c['disposition']} | qtr-sec {c['quarter_section']} | recorded~{c['created_year']} "
            f"(DB date, not legal located date) | src: BLM MLRS Not Closed | APPROX (BLM quarter-section)"
        )
        features.append({
            "type": "polygon",
            "name": f"{c['name']} [APPROX quarter-section]",
            "description": desc,
            "style": "active_claim",
            "coords": clipped_rings,
        })
    return features, claims, n_clipped


# ------------------------------------------------------------- Density D ----
def build_closed_density_features(bbox, refresh):
    claims = blm_claims.fetch_closed_placer(bbox, refresh)
    hexes = geo.make_hex_grid(bbox, cell_size_m=500)
    from shapely.prepared import prep
    from shapely.strtree import STRtree
    hex_prep = [prep(h) for h in hexes]
    hex_tree = STRtree(hexes)

    cell_counts = [0] * len(hexes)
    cell_decades = [Counter() for _ in hexes]
    unmatched = 0
    for c in claims:
        if not c["rings"]:
            continue
        poly = geo.esri_rings_to_polygon(c["rings"])
        centroid = poly.centroid
        placed = False
        for i in hex_tree.query(centroid):
            if hex_prep[i].contains(centroid):
                cell_counts[i] += 1
                decade = (c["created_year"] // 10 * 10) if c["created_year"] else None
                cell_decades[i][decade] += 1
                placed = True
                break
        if not placed:
            unmatched += 1

    features = []
    top_cells = []
    for i, hx in enumerate(hexes):
        count = cell_counts[i]
        if count < 3:
            continue
        if count <= 5:
            style = "density_low"
        elif count <= 10:
            style = "density_med"
        else:
            style = "density_high"
        decades = cell_decades[i]
        decade_str = ", ".join(f"{d}s:{n}" for d, n in sorted(decades.items(), key=lambda kv: (kv[0] is None, kv[0])))
        c = hx.centroid
        desc = clip300(f"Closed placer claims (record-date proxy): {count} total | by decade: {decade_str} | src: BLM MLRS Closed")
        features.append({
            "type": "polygon", "name": f"Closed-claim density: {count}", "description": desc,
            "style": style, "coords": [list(hx.exterior.coords)],
        })
        top_cells.append({"lat": c.y, "lon": c.x, "count": count, "decades": dict(decades)})
    top_cells.sort(key=lambda x: -x["count"])
    return features, top_cells, len(claims), unmatched


# ---------------------------------------------------------------- main -----
def build_area(area_name, refresh=False):
    bbox = AREAS[area_name]
    print(f"\n=== {area_name} {bbox} ===", flush=True)
    out_dir = os.path.join(OUT_DIR, area_name)
    os.makedirs(out_dir, exist_ok=True)
    report = {"area": area_name, "bbox": bbox, "built_at": TODAY}

    print("  fetching reference points...", flush=True)
    ref_feats, ref_lookups = reference_layer.build_reference_features(bbox, refresh)
    report["reference_points"] = ref_lookups

    print("  fetching USMIN...", flush=True)
    usmin_feats, usmin_pts, usmin_polys, usmin_dropped = build_usmin_features(bbox, refresh)
    report["usmin_count"] = len(usmin_feats)
    report["usmin_dropped_types"] = sorted(usmin_dropped)

    print("  fetching MILO/MRDS...", flush=True)
    milo_mrds_feats, combined_gold_points, n_milo, n_mrds_raw, n_mrds_kept = build_milo_mrds_features(bbox, refresh)
    report["milo_count"] = n_milo
    report["mrds_raw_count"] = n_mrds_raw
    report["mrds_kept_after_dedup"] = n_mrds_kept

    print("  fetching active claims...", flush=True)
    active_feats, active_claims_raw, n_claims_clipped = build_active_claims_features(bbox, refresh)
    report["active_claims_count"] = len(active_feats)
    report["active_claims_clipped_to_bbox"] = n_claims_clipped

    print("  fetching closed claims + building density grid...", flush=True)
    density_feats, top_cells, n_closed, n_unmatched = build_closed_density_features(bbox, refresh)
    report["closed_placer_claims_count"] = n_closed
    report["closed_unmatched_to_grid"] = n_unmatched
    report["density_top_cells"] = top_cells[:10]

    print("  fetching land status (BLM/USFS)...", flush=True)
    land_by_agency = land_status.fetch_land_status(bbox, refresh)
    report["land_blm_features"] = len(land_by_agency.get("BLM", []))
    report["land_usfs_features"] = len(land_by_agency.get("USFS", []))

    print("  probing NHD service availability...", flush=True)
    nhd_available = nhd.check_service_available(bbox)
    report["nhd_available"] = nhd_available

    print("  computing open-ground candidates (per-point NHD checks)...", flush=True)
    top_open, nhd_skipped = open_ground.build_candidates(
        usmin_pts, combined_gold_points, land_by_agency, active_claims_raw, nhd_available, area_name, bbox,
        refresh=refresh,
    )
    report["nhd_skipped_for_open_ground"] = nhd_skipped
    open_feats = []
    for c in top_open:
        near = " | NEAR ACTIVE CLAIM (<50m, approx)" if c["near_claim"] else ""
        stream_txt = f"{c['dist_to_stream_m']:.0f}m to stream" if c.get("dist_to_stream_m") is not None else "stream dist n/a"
        desc = clip300(
            f"{c['label']} | agency: {c['agency']} | {stream_txt} | cluster: {c['cluster_density']} nearby{near} | "
            f"src: {c['source']}"
        )
        open_feats.append({
            "type": "point", "name": c["waypoint_name"], "description": desc,
            "style": "open_ground", "coords": (c["lon"], c["lat"]),
        })
    report["open_ground_count"] = len(open_feats)
    report["open_ground_top10"] = [
        {"name": c["waypoint_name"], "lat": c["lat"], "lon": c["lon"], "type": c["ftr_type"], "near_claim": c["near_claim"]}
        for c in top_open[:10]
    ]

    layers = [
        ("My claims & public sites", ref_feats),
        ("Historical workings (USMIN)", usmin_feats),
        ("Mine & prospect sites (MILO/MRDS, gold)", milo_mrds_feats),
        ("Active mining claims (BLM MLRS)", active_feats),
        ("Past claim density (closed placer, 500m hex)", density_feats),
        ("Open ground to sample", open_feats),
    ]
    layers = [(name, feats) for name, feats in layers if feats]

    print("  writing KML/GPX...", flush=True)
    file_reports = render.write_area_outputs(area_name, layers, out_dir, doc_title=AREA_LABELS[area_name])
    report["files"] = file_reports

    with open(os.path.join(out_dir, "build_report.json"), "w") as f:
        json.dump(report, f, indent=2, default=str)

    write_area_readme(report, out_dir, bulletin_notes=BULLETIN_NOTES.get(area_name, ""))

    print(f"  done: {sum(fr['feature_count'] for fr in file_reports)} features across {len(file_reports)} file pair(s)")
    return report


def _kml_coords_outside_bbox(kml_path, bbox, tolerance_deg=0.05):
    """tolerance_deg (~5 km) absorbs expected edge overlap from bbox-intersect
    queries (a claim/hex/land polygon that merely straddles the box edge is
    not a data error) while still catching a genuinely wrong-region feature.
    """
    import xml.etree.ElementTree as ET
    minlon, minlat, maxlon, maxlat = bbox
    ns = {"k": "http://www.opengis.net/kml/2.2"}
    t = ET.parse(kml_path)
    offenders = []
    for coord_el in t.findall(".//k:coordinates", ns):
        text = (coord_el.text or "").strip()
        if not text:
            continue
        for triple in text.split():
            parts = triple.split(",")
            if len(parts) < 2:
                continue
            lon, lat = float(parts[0]), float(parts[1])
            if not (minlon - tolerance_deg <= lon <= maxlon + tolerance_deg
                     and minlat - tolerance_deg <= lat <= maxlat + tolerance_deg):
                offenders.append((lon, lat))
    return offenders


def verify_area(report):
    problems = []
    bbox = report["bbox"]
    for fr in report["files"]:
        if fr["kml_bytes"] > 4 * 1024 * 1024:
            problems.append(f"{fr['kml_path']} exceeds 4MB ({fr['kml_bytes']} bytes)")
        if fr["gpx_bytes"] > 4 * 1024 * 1024:
            problems.append(f"{fr['gpx_path']} exceeds 4MB ({fr['gpx_bytes']} bytes)")
        if fr["feature_count"] > 3000:
            problems.append(f"{fr['kml_path']} exceeds 3000 features ({fr['feature_count']})")
        offenders = _kml_coords_outside_bbox(fr["kml_path"], bbox)
        if offenders:
            problems.append(f"{fr['kml_path']} has {len(offenders)} coordinate(s) outside bbox, e.g. {offenders[:3]}")
    return problems


def run_check_bboxes():
    print("NHD bbox coverage check is documented manually in README.md 'Bounding box notes'.")
    print("(Re-derivable by querying gold_overlays.sources.nhd against a padded bbox per named creek.)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area", default="all")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--check-bboxes", action="store_true")
    ap.add_argument("--rasters", action="store_true", help="also build layer G (lidar) + H (historical topos)")
    ap.add_argument("--skip-vectors", action="store_true", help="with --rasters, skip the KML/GPX build")
    args = ap.parse_args()

    if args.check_bboxes:
        run_check_bboxes()
        return

    areas = list(AREAS.keys()) if args.area == "all" else [args.area]
    all_reports = []
    any_problems = False
    for area in areas:
        if not args.skip_vectors:
            report = build_area(area, refresh=args.refresh)
            problems = verify_area(report)
            if problems:
                any_problems = True
                print(f"  VERIFICATION PROBLEMS for {area}:")
                for p in problems:
                    print(f"    - {p}")
            all_reports.append(report)
        if args.rasters:
            from gold_overlays import rasters
            print(f"  building lidar rasters for {area}...", flush=True)
            rasters.build_lidar_for_area(area, refresh=args.refresh)
            if area in rasters.CLAIM_CLUSTER_AREAS:
                print(f"  fetching historical topos for {area}...", flush=True)
                rasters.build_topo_for_area(area, refresh=args.refresh)

    with open(os.path.join(OUT_DIR, "build_summary.json"), "w") as f:
        json.dump(all_reports, f, indent=2, default=str)

    if any_problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
