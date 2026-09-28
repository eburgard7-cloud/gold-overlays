"""Minimal, dependency-free GPX writer.

onX's phone importer only reads waypoints and tracks, so every polygon
(claim outline, density cell, land-status boundary) is written as a
closed track (first point repeated at the end) instead of a <Polygon>.
"""
from xml.sax.saxutils import escape


def _clip_desc(text, limit=300):
    text = text or ""
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return escape(text)


class GpxWaypoint:
    def __init__(self, lon, lat, name, description="", symbol=None):
        self.lon = lon
        self.lat = lat
        self.name = name
        self.description = description
        self.symbol = symbol

    def to_xml(self):
        sym = f"<sym>{escape(self.symbol)}</sym>" if self.symbol else ""
        return (
            f'<wpt lat="{self.lat:.6f}" lon="{self.lon:.6f}">'
            f"<name>{escape(self.name)}</name>"
            f"<desc>{_clip_desc(self.description)}</desc>"
            f"{sym}"
            "</wpt>"
        )


class GpxTrack:
    """A closed polygon outline stored as a single-segment track."""

    def __init__(self, name, description, ring):
        self.name = name
        self.description = description
        self.ring = ring  # list of (lon, lat), will be closed automatically

    def to_xml(self):
        pts = list(self.ring)
        if pts and pts[0] != pts[-1]:
            pts = pts + [pts[0]]
        seg = "".join(f'<trkpt lat="{y:.6f}" lon="{x:.6f}"></trkpt>' for x, y in pts)
        return (
            "<trk>"
            f"<name>{escape(self.name)}</name>"
            f"<desc>{_clip_desc(self.description)}</desc>"
            f"<trkseg>{seg}</trkseg>"
            "</trk>"
        )


class GpxDocument:
    def __init__(self, name):
        self.name = name
        self.waypoints = []
        self.tracks = []

    def add_waypoint(self, wpt):
        self.waypoints.append(wpt)

    def add_track(self, trk):
        self.tracks.append(trk)

    def feature_count(self):
        return len(self.waypoints) + len(self.tracks)

    def to_xml(self):
        wpts_xml = "".join(w.to_xml() for w in self.waypoints)
        trks_xml = "".join(t.to_xml() for t in self.tracks)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<gpx version="1.1" creator="gold-overlays" '
            'xmlns="http://www.topografix.com/GPX/1/1" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 '
            'http://www.topografix.com/GPX/1/1/gpx.xsd">'
            f"<metadata><name>{escape(self.name)}</name></metadata>"
            f"{wpts_xml}{trks_xml}"
            "</gpx>"
        )

    def write(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_xml())
