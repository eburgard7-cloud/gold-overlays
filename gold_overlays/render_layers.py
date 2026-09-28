"""Turns a single layer's item list (gold_overlays.layers output) into:
  - one onX-format GPX file (primary)
  - one matching KML file (secondary export)
  - a list of CalTopo simplestyle GeoJSON features (collected across all
    layers into one caltopo_<area>.geojson bundle by build.py)
"""
import os

from gold_overlays.onx_gpx import OnxGpxDocument, OnxWaypoint, OnxRoute, MAX_BYTES, MAX_ITEMS
from gold_overlays.kml_writer import KmlDocument, KmlFolder, KmlPlacemark, KmlStyle, point_geometry, polygon_geometry
from gold_overlays import caltopo

_KML_ICON = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"


def _rgba_to_kml_aabbgrr(rgba):
    # rgba(r,g,b,a) -> KML's aabbggrr hex (alpha, blue, green, red)
    import re
    m = re.match(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)", rgba)
    if not m:
        return "ff000000"
    r, g, b, a = int(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4))
    return f"{int(a * 255):02x}{b:02x}{g:02x}{r:02x}"


def write_layer_outputs(area_name, layer_key, layer_title, items, out_dir):
    """Returns (report_dict, caltopo_features)."""
    gpx_doc = OnxGpxDocument(f"{area_name} {layer_title}")
    kml_doc = KmlDocument(f"{area_name} {layer_title}")
    kml_folder = KmlFolder(layer_title)
    caltopo_feats = []

    style_cache = {}

    def _kml_style_for(kind, color):
        key = (kind, color)
        if key in style_cache:
            return style_cache[key]
        style_id = f"s{len(style_cache)}"
        aabbgrr = _rgba_to_kml_aabbgrr(color)
        if kind == "wpt":
            kml_doc.add_style(KmlStyle(style_id, "point", aabbgrr, icon=_KML_ICON, scale=1.0))
        else:
            kml_doc.add_style(KmlStyle(style_id, "polygon", aabbgrr, fill_color_aabbgrr="40" + aabbgrr[2:]))
        style_cache[key] = style_id
        return style_id

    for item in items:
        if item["kind"] == "wpt":
            gpx_doc.add_waypoint(OnxWaypoint(item["lat"], item["lon"], item["name"], item.get("desc", ""),
                                              item["icon"], item["color"]))
            kml_folder.add(KmlPlacemark(item["name"], item.get("desc", ""), _kml_style_for("wpt", item["color"]),
                                         point_geometry(item["lon"], item["lat"])))
            caltopo_feats.append(caltopo.point_feature(item["lon"], item["lat"], item["name"], item.get("desc", ""),
                                                         item["color"]))
        elif item["kind"] == "area":
            pts_latlon = [(y, x) for x, y in item["rings"][0]]
            gpx_doc.add_route(OnxRoute(item["name"], "Area", item["style"], item["color"], pts_latlon))
            kml_folder.add(KmlPlacemark(item["name"], item.get("desc", ""), _kml_style_for("area", item["color"]),
                                         polygon_geometry(item["rings"])))
            caltopo_feats.append(caltopo.polygon_feature(item["rings"], item["name"], item.get("desc", ""),
                                                           item["color"], item["style"]))
        elif item["kind"] == "line":
            pts_latlon = [(y, x) for x, y in item["points"]]
            gpx_doc.add_route(OnxRoute(item["name"], "Line", item["style"], item["color"], pts_latlon))
            kml_folder.add(KmlPlacemark(item["name"], item.get("desc", ""), _kml_style_for("area", item["color"]),
                                         polygon_geometry([item["points"]])))
            caltopo_feats.append(caltopo.line_feature(item["points"], item["name"], item.get("desc", ""),
                                                        item["color"], item["style"]))

    kml_doc.add_folder(kml_folder)

    gpx_path = os.path.join(out_dir, f"{area_name}_{layer_key}.gpx")
    kml_path = os.path.join(out_dir, f"{area_name}_{layer_key}.kml")
    gpx_bytes = gpx_doc.write(gpx_path)
    kml_doc.write(kml_path)
    kml_bytes = os.path.getsize(kml_path)

    report = {
        "layer": layer_key, "gpx_path": gpx_path, "kml_path": kml_path,
        "item_count": gpx_doc.item_count(), "gpx_bytes": gpx_bytes, "kml_bytes": kml_bytes,
        "under_4mb": gpx_bytes <= MAX_BYTES, "under_3000_items": gpx_doc.item_count() <= MAX_ITEMS,
    }
    return report, caltopo_feats
