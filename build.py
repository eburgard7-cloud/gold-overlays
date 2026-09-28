#!/usr/bin/env python3
"""Build onX-ready per-layer GPX/KML overlays (+ CalTopo GeoJSON bundle) for
one or all gold-prospecting areas.

Usage:
    python build.py --area bohemia
    python build.py --area all
    python build.py --area all --refresh      # bypass the on-disk cache
    python build.py --validate-density        # one-time NLSDB density check (task step 3)
"""
import argparse
import datetime
import json
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gold_overlays.config import AREAS, AREA_LABELS, SOURCES
from gold_overlays import geo, layers, render_layers, caltopo
from gold_overlays.http import cached_get_json
from gold_overlays.sources import usmin, mrds, milo, blm_claims, land_status, nhd
from gold_overlays.area_readme import write_area_readme
try:
    from gold_overlays.bulletin_notes import NOTES as BULLETIN_NOTES
except ImportError:
    BULLETIN_NOTES = {}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
TODAY = datetime.date.today().isoformat()

LAYER_TITLES = {
    "1_my_claims": "My claims",
    "2_public": "Public panning sites",
    "3_other_claims": "Other active claims",
    "4_history": "Historical sites",
    "5_scout": "Scout candidates",
    "6_access": "Access routes",
}


def _remove_old_combined_outputs(out_dir, area_name):
    for ext in ("kml", "gpx"):
        for suffix in ("", "_part2", "_part3", "_part4"):
            p = os.path.join(out_dir, f"{area_name}_onx{suffix}.{ext}")
            if os.path.exists(p):
                os.remove(p)


def build_area(area_name, refresh=False):
    bbox = AREAS[area_name]
    print(f"\n=== {area_name} {bbox} ===", flush=True)
    out_dir = os.path.join(OUT_DIR, area_name)
    os.makedirs(out_dir, exist_ok=True)
    _remove_old_combined_outputs(out_dir, area_name)
    report = {"area": area_name, "bbox": bbox, "built_at": TODAY}

    print("  fetching USMIN...", flush=True)
    usmin_pts, usmin_dropped_pt = usmin.fetch_points(bbox, refresh)
    usmin_polys, usmin_dropped_poly = usmin.fetch_polygons(bbox, refresh)
    report["usmin_points"] = len(usmin_pts)
    report["usmin_polygons"] = len(usmin_polys)
    report["usmin_dropped_types"] = sorted(usmin_dropped_pt | usmin_dropped_poly)

    print("  fetching MILO/MRDS...", flush=True)
    milo_sites = milo.fetch_gold_sites(bbox, refresh)
    mrds_sites_raw = mrds.fetch_gold_sites(bbox, refresh)
    mrds_kept = layers.dedup_mrds_against_milo(milo_sites, mrds_sites_raw)
    report["milo_count"] = len(milo_sites)
    report["mrds_raw_count"] = len(mrds_sites_raw)
    report["mrds_kept_after_dedup"] = len(mrds_kept)

    print("  fetching active claims...", flush=True)
    active_claims_raw = blm_claims.fetch_active(bbox, refresh)
    report["active_claims_raw_count"] = len(active_claims_raw)

    print("  fetching land status (BLM/USFS)...", flush=True)
    land_by_agency = land_status.fetch_land_status(bbox, refresh)
    report["land_blm_features"] = len(land_by_agency.get("BLM", []))
    report["land_usfs_features"] = len(land_by_agency.get("USFS", []))

    print("  probing NHD service availability...", flush=True)
    nhd_available = nhd.check_service_available(bbox)
    report["nhd_available"] = nhd_available

    print("  building layer 1 (my claims)...", flush=True)
    layer1_items, my_claim_serials, l1_report = layers.build_layer1_my_claims(bbox, area_name, refresh)
    report["layer1_my_claims"] = l1_report

    print("  building layer 2 (public)...", flush=True)
    layer2_items, l2_report = layers.build_layer2_public(bbox, area_name)
    report["layer2_public"] = l2_report

    print("  building layer 3 (other active claims)...", flush=True)
    layer3_items, l3_report = layers.build_layer3_other_claims(active_claims_raw, my_claim_serials, bbox)
    report["layer3_other_claims"] = l3_report

    print("  building layer 4 (deduped history)...", flush=True)
    layer4_items, l4_report = layers.build_layer4_history(usmin_pts, usmin_polys, milo_sites, mrds_kept, bbox)
    report["layer4_history"] = l4_report

    print("  building layer 5 (scout / open ground)...", flush=True)
    combined_gold_points = []
    for s in milo_sites:
        s2 = dict(s)
        s2["_source"] = "MILO"
        combined_gold_points.append(s2)
    for m in mrds_kept:
        m2 = dict(m)
        m2["_source"] = "MRDS"
        combined_gold_points.append(m2)
    layer5_items, l5_report = layers.build_layer5_scout(
        usmin_pts, combined_gold_points, mrds_kept, land_by_agency, active_claims_raw,
        nhd_available, area_name, bbox, refresh=refresh,
    )
    report["layer5_scout"] = l5_report

    print("  building layer 6 (access routes)...", flush=True)
    layer6_items, l6_report = layers.build_layer6_access(area_name)
    report["layer6_access"] = l6_report

    print("  writing per-layer GPX/KML + CalTopo bundle...", flush=True)
    layer_defs = [
        ("1_my_claims", layer1_items), ("2_public", layer2_items),
        ("3_other_claims", layer3_items), ("4_history", layer4_items),
        ("5_scout", layer5_items), ("6_access", layer6_items),
    ]
    file_reports = []
    caltopo_features = []
    for key, items in layer_defs:
        if not items:
            continue
        rep, feats = render_layers.write_layer_outputs(area_name, key, LAYER_TITLES[key], items, out_dir)
        file_reports.append(rep)
        caltopo_features.extend(feats)
    report["files"] = file_reports

    caltopo_path = os.path.join(out_dir, f"caltopo_{area_name}.geojson")
    caltopo.write_bundle(caltopo_features, caltopo_path)
    report["caltopo_path"] = caltopo_path
    report["caltopo_feature_count"] = len(caltopo_features)

    with open(os.path.join(out_dir, "build_report.json"), "w") as f:
        json.dump(report, f, indent=2, default=str)

    write_area_readme(report, out_dir, bulletin_notes=BULLETIN_NOTES.get(area_name, ""))

    total_items = sum(fr["item_count"] for fr in file_reports)
    print(f"  done: {total_items} items across {len(file_reports)} layer file(s)")
    return report


# ------------------------------------------------------------- verify ------
def _gpx_items_and_bbox_offenders(gpx_path, bbox, tolerance_deg=0.01):
    minlon, minlat, maxlon, maxlat = bbox
    ns = {"g": "http://www.topografix.com/GPX/1/1"}
    t = ET.parse(gpx_path)
    root = t.getroot()
    offenders = []
    icon_or_style_missing = []
    n_items = 0
    for wpt in root.findall("g:wpt", ns):
        n_items += 1
        lat, lon = float(wpt.get("lat")), float(wpt.get("lon"))
        if not (minlon - tolerance_deg <= lon <= maxlon + tolerance_deg and
                minlat - tolerance_deg <= lat <= maxlat + tolerance_deg):
            offenders.append((lon, lat))
        icon_el = wpt.find(".//{http://www.onxmaps.com}icon")
        if icon_el is None or not (icon_el.text or "").strip():
            icon_or_style_missing.append(wpt.findtext("g:name", default="?", namespaces=ns))
    for rte in root.findall("g:rte", ns):
        n_items += 1
        type_el = rte.find("g:type", ns)
        style_el = rte.find(".//{http://www.onxmaps.com}style")
        color_el = rte.find(".//{http://www.onxmaps.com}color")
        if type_el is None or style_el is None or color_el is None:
            icon_or_style_missing.append(rte.findtext("g:name", default="?", namespaces=ns))
        for pt in rte.findall("g:rtept", ns):
            lat, lon = float(pt.get("lat")), float(pt.get("lon"))
            if not (minlon - tolerance_deg <= lon <= maxlon + tolerance_deg and
                    minlat - tolerance_deg <= lat <= maxlat + tolerance_deg):
                offenders.append((lon, lat))
    return n_items, offenders, icon_or_style_missing


def verify_area(report):
    from gold_overlays.onx_style import ALL_CONFIRMED_COLORS, ALL_CONFIRMED_ICONS

    problems = []
    bbox = report["bbox"]
    for fr in report["files"]:
        if fr["gpx_bytes"] > 4 * 1024 * 1024:
            problems.append(f"{fr['gpx_path']} exceeds 4MB ({fr['gpx_bytes']} bytes)")
        if fr["item_count"] > 3000:
            problems.append(f"{fr['gpx_path']} exceeds 3000 items ({fr['item_count']})")
        try:
            ET.parse(fr["gpx_path"])
        except ET.ParseError as e:
            problems.append(f"{fr['gpx_path']} failed to parse: {e}")
            continue
        n_items, offenders, missing = _gpx_items_and_bbox_offenders(fr["gpx_path"], bbox)
        if offenders:
            problems.append(f"{fr['gpx_path']} has {len(offenders)} coordinate(s) outside bbox, e.g. {offenders[:3]}")
        if missing:
            problems.append(f"{fr['gpx_path']} has {len(missing)} item(s) missing onx:icon/type+style+color: {missing[:3]}")
        # name length + color/icon whitelist check via raw text scan
        with open(fr["gpx_path"], encoding="utf-8") as f:
            text = f.read()
        import re
        for name in re.findall(r"<name>(.*?)</name>", text):
            from xml.sax.saxutils import unescape
            if len(unescape(name)) > 32:
                problems.append(f"{fr['gpx_path']} has a name over 32 chars: {unescape(name)!r}")
        for icon in re.findall(r"<onx:icon>(.*?)</onx:icon>", text):
            from xml.sax.saxutils import unescape
            if unescape(icon) not in ALL_CONFIRMED_ICONS:
                problems.append(f"{fr['gpx_path']} uses unconfirmed onx:icon {icon!r}")
        for color in re.findall(r"<onx:color>(.*?)</onx:color>", text):
            from xml.sax.saxutils import unescape
            if unescape(color) not in ALL_CONFIRMED_COLORS:
                problems.append(f"{fr['gpx_path']} uses unconfirmed onx:color {color!r}")

    if report["layer4_history"]["final_count"] > 150:
        problems.append(f"layer4_history has {report['layer4_history']['final_count']} > 150 cap")
    if report["layer5_scout"]["count"] > 10:
        problems.append(f"layer5_scout has {report['layer5_scout']['count']} > 10 cap")
    return problems


SPOT_CHECK_SERIALS = {"ORMC171094", "ORMC30445", "ORMC163049"}


def verify_spot_check_claims(all_reports):
    found = set()
    for report in all_reports:
        path = os.path.join(OUT_DIR, report["area"], f"{report['area']}_1_my_claims.gpx")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for serial in SPOT_CHECK_SERIALS:
            if serial in text:
                found.add(serial)
    missing = SPOT_CHECK_SERIALS - found
    return missing


# --------------------------------------------- closed-claim density check --
def validate_closed_claim_density():
    """Task step 3: try gis.blm.gov/nlsdb NLSDB_LND_HIST (layer 3, an
    action-history TABLE with no geometry of its own) via its 1:1 join to
    layer 0 ('Case Feature Layer', which does carry full case geometry --
    active + closed + historical, all record types). Keep/use it only if
    Bohemia's case count lands within 3x of The Diggings' ~1,550 claims
    estimate; otherwise it stays out of every output (it already is, since
    the new 6-layer style guide has no density layer) and this is documented.
    """
    url = SOURCES["nlsdb_case"]["url"]
    bbox = AREAS["bohemia"]
    params = {
        "geometry": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "geometryType": "esriGeometryEnvelope", "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects", "returnCountOnly": "true", "f": "json",
    }
    try:
        data = cached_get_json(url + "/query", params, timeout=60)
        count = data.get("count")
    except Exception as e:
        count = None
        print(f"NLSDB case-count query failed: {e}")

    diggings_estimate = 1550
    old_mlrs_closed_count = 8  # from the previous build's BLM_Natl_MLRS_Mining_Claims_Closed pull
    result = {
        "bohemia_nlsdb_case_count": count,
        "diggings_estimate": diggings_estimate,
        "old_mlrs_closed_placer_count": old_mlrs_closed_count,
        "within_3x": (diggings_estimate / 3 <= count <= diggings_estimate * 3) if count is not None else False,
    }
    lines = [
        "# Closed-claim density validation (task step 3)", "",
        f"- `BLM_Natl_MLRS_Mining_Claims_Closed` (old approach): {old_mlrs_closed_count} placer claims for Bohemia "
        "-- confirmed to lack legacy geometry for most historical claims.",
        f"- `gis.blm.gov/nlsdb/.../MiningClaims/MapServer` layer 3 (`NLSDB_LND_HIST`) is an action-history **table** "
        "with no geometry of its own; it joins 1:1 to layer 0 (`Case Feature Layer`, `CSE_OBJECTID`) which *does* "
        "carry full case geometry for every record type (active, closed, historical, patented, excluded, conveyed).",
        f"- Layer 0 case count intersecting the Bohemia bbox: **{count}**.",
        f"- The Diggings' estimate for Bohemia: ~{diggings_estimate}.",
        f"- Ratio: {count / diggings_estimate:.2f}x " + ("(within 3x -- PASS)" if result["within_3x"] else "(NOT within 3x -- FAIL)")
        if count is not None else "- Query failed -- could not validate.",
        "",
        "**Decision:** " + (
            "The NLSDB Case Feature Layer is plausible for Bohemia and could support a future "
            "'closed-claim density' layer. It is NOT added as a 7th onX layer in this build because "
            "the style guide (section 1 of the task) defines only the 6 layers 1_my_claims..6_access; "
            "no density layer is in scope for onX output. This validation is recorded here for the record."
            if result["within_3x"] else
            "NLSDB does not check out within 3x either -- the closed-claim density concept stays out of "
            "every output, as it already was under the new 6-layer style guide."
        ),
        "",
    ]
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "closed_claim_density_validation.md"), "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area", default="all")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--validate-density", action="store_true")
    ap.add_argument("--rasters", action="store_true", help="also build layer G (lidar) + H (historical topos)")
    ap.add_argument("--skip-vectors", action="store_true", help="with --rasters, skip the GPX/KML build")
    args = ap.parse_args()

    if args.validate_density:
        validate_closed_claim_density()
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

    if not args.skip_vectors:
        with open(os.path.join(OUT_DIR, "build_summary.json"), "w") as f:
            json.dump(all_reports, f, indent=2, default=str)
        if args.area == "all":
            missing = verify_spot_check_claims(all_reports)
            if missing:
                any_problems = True
                print(f"VERIFICATION PROBLEM: spot-check claims missing from 1_my_claims outputs: {missing}")
            else:
                print("Spot-check claims OK: all 3 present in their area's 1_my_claims.gpx")

    if any_problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
