"""onX-format GPX writer -- matches onx_samples/*.gpx exactly:

  <gpx ... xmlns:onx="http://www.onxmaps.com" version="1.1" creator="...">
    <wpt lat lon><name/><desc/><extensions><onx:icon/><onx:color/></extensions></wpt>
    <rte><name/><type>Area|Line</type>
         <extensions><onx:style/><onx:weight/><onx:color/></extensions>
         <rtept lat lon/>...</rte>

Areas repeat their first point as their last point. Only icons/colors from
gold_overlays.onx_style's confirmed sets are ever written.
"""
import os
from xml.sax.saxutils import escape

from gold_overlays.onx_style import safe_icon, safe_color

NOTE_LIMIT = 500  # onX hard cap is 512; leave headroom
NAME_LIMIT = 32
MAX_ITEMS = 3000
MAX_BYTES = 4 * 1024 * 1024


def clip_name(name):
    name = (name or "").strip()
    return name if len(name) <= NAME_LIMIT else name[: NAME_LIMIT - 1].rstrip() + "…"


def clip_note(text):
    text = (text or "").strip()
    return text if len(text) <= NOTE_LIMIT else text[: NOTE_LIMIT - 1].rstrip() + "…"


class OnxWaypoint:
    def __init__(self, lat, lon, name, desc, icon, color):
        self.lat = lat
        self.lon = lon
        self.name = clip_name(name)
        self.desc = clip_note(desc)
        self.icon = safe_icon(icon)
        self.color = safe_color(color)

    def to_xml(self):
        return (
            f'<wpt lat="{self.lat:.6f}" lon="{self.lon:.6f}">'
            f"<name>{escape(self.name)}</name>"
            f"<desc>{escape(self.desc)}</desc>"
            "<extensions>"
            f"<onx:icon>{escape(self.icon)}</onx:icon>"
            f"<onx:color>{escape(self.color)}</onx:color>"
            "</extensions>"
            "</wpt>"
        )


class OnxRoute:
    """rte_type: 'Area' or 'Line'. style: 'solid', 'dot', or 'dash'."""

    def __init__(self, name, rte_type, style, color, points, weight=4.0):
        assert rte_type in ("Area", "Line")
        assert style in ("solid", "dot", "dash")
        self.name = clip_name(name)
        self.rte_type = rte_type
        self.style = style
        self.color = safe_color(color)
        self.weight = weight
        pts = list(points)
        if rte_type == "Area" and pts and pts[0] != pts[-1]:
            pts = pts + [pts[0]]
        self.points = pts  # list of (lat, lon)

    def to_xml(self):
        pts_xml = "".join(f'<rtept lat="{lat:.6f}" lon="{lon:.6f}"></rtept>' for lat, lon in self.points)
        return (
            "<rte>"
            f"<name>{escape(self.name)}</name>"
            f"<type>{self.rte_type}</type>"
            "<extensions>"
            f"<onx:style>{self.style}</onx:style>"
            f"<onx:weight>{self.weight}</onx:weight>"
            f"<onx:color>{escape(self.color)}</onx:color>"
            "</extensions>"
            f"{pts_xml}"
            "</rte>"
        )


class OnxGpxDocument:
    def __init__(self, name):
        self.name = name
        self.waypoints = []
        self.routes = []

    def add_waypoint(self, wpt):
        self.waypoints.append(wpt)

    def add_route(self, rte):
        self.routes.append(rte)

    def item_count(self):
        return len(self.waypoints) + len(self.routes)

    def to_xml(self):
        body = "".join(w.to_xml() for w in self.waypoints) + "".join(r.to_xml() for r in self.routes)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns="http://www.topografix.com/GPX/1/1" '
            'xmlns:onx="http://www.onxmaps.com" '
            'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 '
            'http://www.topografix.com/GPX/1/1/gpx.xsd" '
            'version="1.1" creator="onXmaps hunt ios">'
            f"{body}"
            "</gpx>"
        )

    def write(self, path):
        xml = self.to_xml()
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)
        return len(xml.encode("utf-8"))
