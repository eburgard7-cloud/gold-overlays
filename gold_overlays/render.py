"""Turns generic layer/feature lists into onX-ready KML+GPX file pairs,
splitting across multiple files to respect onX's 4 MB / 3000-feature caps.
"""
import os

from gold_overlays.kml_writer import KmlDocument, KmlFolder, KmlPlacemark, KmlStyle, point_geometry, polygon_geometry
from gold_overlays.gpx_writer import GpxDocument, GpxWaypoint, GpxTrack

MAX_FEATURES = 3000
MAX_BYTES = 4 * 1024 * 1024
SAFETY_MARGIN_BYTES = int(MAX_BYTES * 0.9)  # leave headroom before hard cap

# style_key -> (kml_color_aabbggrr, kml_fill_aabbggrr_or_None, kind, icon_or_None, scale)
STYLES = {
    "my_claim": ("ff00a5ff", None, "point", "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png", 1.0),
    "public_site": ("ff008000", None, "point", "http://maps.google.com/mapfiles/kml/paddle/grn-circle.png", 1.0),
    "usmin": ("ff000000", None, "point", "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png", 0.7),
    "usmin_polygon": ("ff000000", "40000000", "polygon", None, None),
    "milo_gold": ("ff00d7ff", None, "point", "http://maps.google.com/mapfiles/kml/shapes/mining.png", 1.0),
    "site_other": ("ff808080", None, "point", "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png", 0.8),
    "active_claim": ("ff0000ff", "660000ff", "polygon", None, None),
    "density_low": ("ff00ffff", "9900ffff", "polygon", None, None),
    "density_med": ("ff00a5ff", "9900a5ff", "polygon", None, None),
    "density_high": ("ff0000ff", "990000ff", "polygon", None, None),
    "open_ground": ("ff00ff00", None, "point", "http://maps.google.com/mapfiles/kml/shapes/star.png", 1.1),
}

GPX_SYMBOLS = {
    "my_claim": "Flag, Orange",
    "public_site": "Flag, Green",
    "usmin": "Dot",
    "usmin_polygon": "Dot",
    "milo_gold": "Bar",
    "site_other": "Dot",
    "active_claim": "Building",
    "density_low": "Building",
    "density_med": "Building",
    "density_high": "Building",
    "open_ground": "Star",
}


def _kml_size_estimate(doc):
    return len(doc.to_xml().encode("utf-8"))


def _make_style_objs():
    styles = []
    for key, (color, fill, kind, icon, scale) in STYLES.items():
        styles.append(KmlStyle(key, kind, color, fill_color_aabbgrr=fill, icon=icon, scale=scale or 1.0))
    return styles


def _feature_to_kml_placemark(feat):
    style = feat["style"]
    if feat["type"] == "point":
        lon, lat = feat["coords"]
        geom = point_geometry(lon, lat)
    else:
        geom = polygon_geometry(feat["coords"])
    return KmlPlacemark(feat["name"], feat.get("description", ""), style, geom)


def _feature_to_gpx(feat):
    style = feat["style"]
    sym = GPX_SYMBOLS.get(style)
    if feat["type"] == "point":
        lon, lat = feat["coords"]
        return GpxWaypoint(lon, lat, feat["name"], feat.get("description", ""), symbol=sym)
    else:
        outer_ring = feat["coords"][0]
        return GpxTrack(feat["name"], feat.get("description", ""), outer_ring)


def write_area_outputs(area_name, layers, out_dir, doc_title=None):
    """layers: list of (layer_name, [feature, ...]).
    Returns a report dict used for the README + verification section.
    """
    os.makedirs(out_dir, exist_ok=True)
    doc_title = doc_title or area_name

    # Flatten to (layer_name, feature) pairs, splitting any single layer
    # that alone exceeds MAX_FEATURES into '(part N)' sub-layers.
    chunks = []  # list of (layer_name, [features])
    for layer_name, feats in layers:
        if len(feats) <= MAX_FEATURES:
            chunks.append((layer_name, feats))
        else:
            for i in range(0, len(feats), MAX_FEATURES):
                part = i // MAX_FEATURES + 1
                chunks.append((f"{layer_name} (part {part})", feats[i : i + MAX_FEATURES]))

    # Greedily pack chunks into files respecting feature count; size is
    # checked after building and forces an additional split if exceeded.
    files = []  # list of list-of-(layer_name, feats)
    current = []
    current_count = 0
    for layer_name, feats in chunks:
        if current and current_count + len(feats) > MAX_FEATURES:
            files.append(current)
            current = []
            current_count = 0
        current.append((layer_name, feats))
        current_count += len(feats)
    if current:
        files.append(current)

    file_reports = []
    file_idx = 0
    fi = 0
    while fi < len(files):
        group = files[fi]
        suffix = "" if len(files) == 1 else f"_part{file_idx + 1}"
        kml_doc = KmlDocument(f"{doc_title}{suffix}")
        for s in _make_style_objs():
            kml_doc.add_style(s)
        gpx_doc = GpxDocument(f"{doc_title}{suffix}")
        for layer_name, feats in group:
            folder = KmlFolder(layer_name)
            for feat in feats:
                folder.add(_feature_to_kml_placemark(feat))
                gpx_item = _feature_to_gpx(feat)
                if isinstance(gpx_item, GpxWaypoint):
                    gpx_doc.add_waypoint(gpx_item)
                else:
                    gpx_doc.add_track(gpx_item)
            kml_doc.add_folder(folder)

        size = _kml_size_estimate(kml_doc)
        if size > SAFETY_MARGIN_BYTES and len(group) > 1:
            # split this group of layers in half and retry
            mid = len(group) // 2
            files[fi : fi + 1] = [group[:mid], group[mid:]]
            continue
        if size > SAFETY_MARGIN_BYTES and len(group) == 1:
            # single oversized layer chunk: split its feature list in half
            layer_name, feats = group[0]
            if len(feats) > 1:
                mid = len(feats) // 2
                files[fi : fi + 1] = [
                    [(f"{layer_name} (part a)", feats[:mid])],
                    [(f"{layer_name} (part b)", feats[mid:])],
                ]
                continue

        kml_path = os.path.join(out_dir, f"{area_name}_onx{suffix}.kml")
        gpx_path = os.path.join(out_dir, f"{area_name}_onx{suffix}.gpx")
        kml_doc.write(kml_path)
        gpx_doc.write(gpx_path)
        file_reports.append({
            "kml_path": kml_path,
            "gpx_path": gpx_path,
            "kml_bytes": os.path.getsize(kml_path),
            "gpx_bytes": os.path.getsize(gpx_path),
            "feature_count": kml_doc.feature_count(),
            "layers": [ln for ln, _ in group],
        })
        file_idx += 1
        fi += 1

    return file_reports
