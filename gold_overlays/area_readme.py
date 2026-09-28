"""Generates out/<area>/README.md from a build_area() report dict."""
import os

LAYER_LEGEND = [
    ("1_my_claims", "Mineral Site (pin) / filled Area", "yellow", "solid",
     "WVM/BMOA club claims -- ours"),
    ("2_public", "Location (pin)", "black", "n/a (points only)",
     "Public gold-panning sites open to anyone"),
    ("3_other_claims", "Area only, no pins", "red", "dotted",
     "Other active BLM claims -- don't dig here"),
    ("4_history", "Mineral Site (placer/tailings/hydraulic) / Location (adit/shaft/pit)", "black", "n/a (points only)",
     "Deduped historical workings"),
    ("5_scout", "Location (pin)", "red", "n/a (points only)",
     "Open-ground candidates worth scouting"),
    ("6_access", "Line", "black", "dash/dot",
     "Claim-access route (only where a real source describes one)"),
]


def _legend_table():
    lines = ["| layer | icon | color | style | meaning |", "|---|---|---|---|---|"]
    for key, icon, color, style, meaning in LAYER_LEGEND:
        lines.append(f"| {key} | {icon} | {color} | {style} | {meaning} |")
    return lines


def write_area_readme(report, out_dir, bulletin_notes=""):
    area = report["area"]
    bbox = report["bbox"]
    lines = []
    lines.append(f"# {area} -- gold-overlay build report")
    lines.append("")
    lines.append(f"Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `{bbox}`")
    lines.append(f"Built: {report['built_at']}")
    lines.append("")

    lines.append("## Legend")
    lines.append("")
    lines.extend(_legend_table())
    lines.append("")
    lines.append(
        "Only confirmed onX icons/colors are used: icons `Mineral Site` / `Location`; colors yellow "
        "`rgba(255,255,0,1)`, red `rgba(255,51,0,1)`, black `rgba(0,0,0,1)`. Green for confirmed public "
        "sites and any other icon/color in `onx_samples/onx_test.gpx` is a GUESS pending "
        "`onx_samples/STYLE_RESULTS.md` -- not used until confirmed (see top-level README)."
    )
    lines.append("")

    lines.append("## Import steps (phone)")
    lines.append("")
    lines.append("1. onX app -> **My Content** -> **Import** -> choose one `<area>_<layer>.gpx` file.")
    lines.append("2. After import, select all the newly-imported items -> **Add to folder** -> "
                 f'name it `"{area} <layer>"` (e.g. `"{area} 1_my_claims"`).')
    lines.append("3. Repeat per layer file. Each file is small and single-purpose so the folder step stays quick.")
    lines.append("")

    lines.append("## Output files")
    for fr in report["files"]:
        ok = "OK" if (fr["under_4mb"] and fr["under_3000_items"]) else "OVER LIMIT"
        lines.append(
            f"- `{os.path.basename(fr['gpx_path'])}` (+ `{os.path.basename(fr['kml_path'])}` secondary) -- "
            f"{fr['item_count']} items, {fr['gpx_bytes']/1024:.1f} KB GPX [{ok}]"
        )
    if report.get("caltopo_path"):
        lines.append(f"- `{os.path.basename(report['caltopo_path'])}` -- CalTopo bundle, "
                     f"{report['caltopo_feature_count']} features, all layers combined")
    lines.append("")

    lines.append("## Layer counts")
    lines.append(f"- 1_my_claims: {report['layer1_my_claims']['count']}")
    lines.append(f"- 2_public: {report['layer2_public']['count']} ({report['layer2_public']['corridor_areas_skipped']})")
    lines.append(f"- 3_other_claims: {report['layer3_other_claims']['count']} "
                 f"(excluded as ours: {report['layer3_other_claims']['excluded_as_my_claims']}, "
                 f"clipped to bbox: {report['layer3_other_claims']['clipped_to_bbox']})")
    l4 = report["layer4_history"]
    lines.append(f"- 4_history: {l4['final_count']} / {l4['max_allowed']} cap "
                 f"(raw records: {l4['raw_records']}, clusters before cap: {l4['clusters_before_cap']}, "
                 f"dropped generic MILO far from USMIN: {l4['dropped_generic_milo_far_from_usmin']}, "
                 f"dropped prospect pits over cap: {l4['dropped_prospect_pits_over_cap']})")
    l5 = report["layer5_scout"]
    lines.append(f"- 5_scout: {l5['count']} / 10 cap (candidate pool: {l5['candidate_pool']}, "
                 f"NHD stream filter skipped: {l5['nhd_skipped']}, land checks: {l5['land_checks']})")
    lines.append(f"- 6_access: {report['layer6_access']['count']} ({report['layer6_access']['reason']})")
    lines.append("")

    lines.append("## My claims (layer 1) resolution detail")
    for name, kind, note in report["layer1_my_claims"]["lookups"]:
        lines.append(f"- **{name}** -- {kind} ({note})")
    lines.append("")

    lines.append("## Caveats specific to this area")
    lines.append("- BLM claim polygons are approximate to the quarter-section (not drawn from a legal survey).")
    lines.append("- Layer 1 'directions' field: no club handbook source exists in this repo, so it reads "
                 "'not available' rather than being invented.")
    lines.append("- Layer 2 public-corridor Areas are skipped (no verified extent-polygon source) -- only "
                 "point pins are rendered for public sites.")
    lines.append("- Layer 5 scout candidates' final tiebreaker is distance-to-stream, not distance-to-road "
                 "(no road dataset fetched in this build).")
    if report["layer5_scout"]["nhd_skipped"]:
        lines.append("- **NHD flowline service was unreachable for this area** -- the 150m stream-proximity "
                      "filter was skipped for layer 5; treat scout candidates here as unfiltered by stream distance.")
    lc = report["layer5_scout"]["land_checks"]
    if lc.get("unverifiable"):
        lines.append(f"- {lc['unverifiable']} scout candidate(s) could not be re-verified against BLM SMA "
                      "point-level land status (service error) -- flagged '(check owner)' in their description.")
    lines.append("- Layer 6 access routes: skipped, no handbook/directions source data exists in this repo.")
    lines.append("- MRDS attribute detail is limited to what its public WFS exposes (name/status/commodity codes).")
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
