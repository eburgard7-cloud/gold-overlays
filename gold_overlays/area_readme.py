"""Generates out/<area>/README.md from a build_area() report dict."""
import os


def write_area_readme(report, out_dir, bulletin_notes=""):
    area = report["area"]
    bbox = report["bbox"]
    lines = []
    lines.append(f"# {area} -- gold-overlay build report")
    lines.append("")
    lines.append(f"Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `{bbox}`")
    lines.append(f"Built: {report['built_at']}")
    lines.append("")

    lines.append("## Output files")
    for fr in report["files"]:
        lines.append(f"- `{os.path.basename(fr['kml_path'])}` / `{os.path.basename(fr['gpx_path'])}` -- "
                     f"{fr['feature_count']} features, {fr['kml_bytes']/1024:.0f} KB KML / {fr['gpx_bytes']/1024:.0f} KB GPX")
        lines.append(f"  - layers: {', '.join(fr['layers'])}")
    lines.append("")

    lines.append("## Layer counts")
    lines.append(f"- My claims & public sites: {len(report['reference_points'])}")
    lines.append(f"- USMIN historical workings: {report['usmin_count']} (dropped types: {', '.join(report['usmin_dropped_types']) or 'none'})")
    lines.append(f"- MILO-4 gold sites: {report['milo_count']}")
    lines.append(f"- MRDS gold sites (raw / kept after MILO dedup): {report['mrds_raw_count']} / {report['mrds_kept_after_dedup']}")
    lines.append(f"- Active BLM claims (Not Closed): {report['active_claims_count']}")
    lines.append(f"- Closed placer claims fetched: {report['closed_placer_claims_count']} "
                 f"(unmatched to any 500m hex: {report['closed_unmatched_to_grid']})")
    lines.append(f"- Land status polygons fetched: BLM={report['land_blm_features']}, USFS={report['land_usfs_features']}")
    lines.append(f"- NHD service reachable for this area: {report['nhd_available']}"
                 + (" -- 150m stream filter SKIPPED for open ground" if report.get('nhd_skipped_for_open_ground') else ""))
    lines.append(f"- Open ground to sample: {report['open_ground_count']} waypoints")
    lines.append("")

    lines.append("## My claims & public sites (reference table)")
    for name, kind, note in report["reference_points"]:
        lines.append(f"- **{name}** -- {kind} ({note})")
    lines.append("")

    lines.append("## Past claim density -- top cells")
    lines.append("")
    lines.append("| lat | lon | total closed placer claims | by decade |")
    lines.append("|---|---|---|---|")
    for cell in report["density_top_cells"]:
        decades = ", ".join(f"{d}s:{n}" for d, n in sorted(cell["decades"].items(), key=lambda kv: (kv[0] is None, kv[0])))
        lines.append(f"| {cell['lat']:.4f} | {cell['lon']:.4f} | {cell['count']} | {decades} |")
    lines.append("")

    lines.append("## Open ground to sample -- top 10")
    lines.append("")
    lines.append("| waypoint | lat | lon | feature type | near active claim |")
    lines.append("|---|---|---|---|---|")
    for c in report["open_ground_top10"]:
        lines.append(f"| {c['name']} | {c['lat']:.5f} | {c['lon']:.5f} | {c['type']} | {c['near_claim']} |")
    lines.append("")

    lines.append("## Caveats specific to this area")
    lines.append("- BLM claim polygons are approximate to the quarter-section; every claim polygon is labeled")
    lines.append("  `[APPROX quarter-section]` in its name and description.")
    lines.append("- 'Closed-claim density' decade buckets use the MLRS `Created` (database record) date as a proxy for")
    lines.append("  located date -- the public feature service does not expose a true located/last-action date.")
    lines.append("- 'Open ground' ranking's final tiebreaker is distance-to-stream, not distance-to-road (no road")
    lines.append("  dataset was fetched in this build).")
    if report.get("nhd_skipped_for_open_ground"):
        lines.append("- **NHD flowline service was unreachable for this area** -- the 150m stream-proximity filter was")
        lines.append("  skipped for layer F; treat 'open ground' candidates here as unfiltered by stream distance.")
    lines.append("- MRDS attribute detail is limited to what its public WFS exposes (name/status/commodity codes);")
    lines.append("  full deposit-type/production detail lives on the per-site page linked in each description.")
    lines.append("")

    if bulletin_notes:
        lines.append("## DOGAMI Bulletin 61 notes")
        lines.append("")
        lines.append(bulletin_notes)
        lines.append("")

    path = os.path.join(out_dir, "README.md")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path
