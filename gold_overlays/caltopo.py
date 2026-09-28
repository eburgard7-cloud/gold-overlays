"""CalTopo-ready GeoJSON bundle: one FeatureCollection per area with all
layers combined, using simplestyle-spec properties CalTopo understands
(marker-color, marker-symbol, stroke, stroke-width, fill, fill-opacity,
title, description).
"""
import json

from gold_overlays.onx_style import COLOR_YELLOW, COLOR_RED, COLOR_BLACK

_RGBA_HEX = {
    COLOR_YELLOW: "#ffff00",
    COLOR_RED: "#ff3300",
    COLOR_BLACK: "#000000",
}


def _hex(color):
    return _RGBA_HEX.get(color, "#000000")


def _dasharray(style):
    return {"dot": "1,6", "dash": "8,6"}.get(style)


def point_feature(lon, lat, name, description, color, marker_symbol="circle"):
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "title": name,
            "description": description,
            "marker-color": _hex(color),
            "marker-symbol": marker_symbol,
        },
    }


def polygon_feature(rings, name, description, color, style="solid"):
    coords = [[[x, y] for x, y in ring] for ring in rings]
    props = {
        "title": name,
        "description": description,
        "stroke": _hex(color),
        "stroke-width": 2,
        "fill": _hex(color),
        "fill-opacity": 0.25 if style == "solid" else 0.05,
    }
    da = _dasharray(style)
    if da:
        props["stroke-dasharray"] = da
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": coords},
        "properties": props,
    }


def line_feature(points, name, description, color, style="solid"):
    coords = [[x, y] for x, y in points]
    props = {
        "title": name,
        "description": description,
        "stroke": _hex(color),
        "stroke-width": 3,
    }
    da = _dasharray(style)
    if da:
        props["stroke-dasharray"] = da
    return {
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": coords},
        "properties": props,
    }


def write_bundle(features, out_path):
    fc = {"type": "FeatureCollection", "features": features}
    with open(out_path, "w") as f:
        json.dump(fc, f)
    return out_path
