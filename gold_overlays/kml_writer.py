"""Minimal, dependency-free KML writer (folders, styled points/polygons)."""
from xml.sax.saxutils import escape


def _clip_desc(text, limit=300):
    text = text or ""
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return escape(text)


class KmlStyle:
    def __init__(self, style_id, kind, color_aabbgrr, fill_color_aabbgrr=None, icon=None, scale=1.0):
        self.id = style_id
        self.kind = kind  # "point" or "polygon"
        self.color = color_aabbgrr
        self.fill_color = fill_color_aabbgrr
        self.icon = icon
        self.scale = scale

    def to_xml(self):
        if self.kind == "polygon":
            fill = self.fill_color or self.color
            return (
                f'<Style id="{self.id}">'
                f'<LineStyle><color>{self.color}</color><width>2</width></LineStyle>'
                f'<PolyStyle><color>{fill}</color></PolyStyle>'
                f"</Style>"
            )
        else:
            icon_href = self.icon or "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
            return (
                f'<Style id="{self.id}">'
                f'<IconStyle><color>{self.color}</color><scale>{self.scale}</scale>'
                f'<Icon><href>{icon_href}</href></Icon></IconStyle>'
                f"</Style>"
            )


class KmlPlacemark:
    def __init__(self, name, description, style_id, geometry_xml):
        self.name = name
        self.description = description
        self.style_id = style_id
        self.geometry_xml = geometry_xml

    def to_xml(self):
        return (
            "<Placemark>"
            f"<name>{escape(self.name)}</name>"
            f"<description>{_clip_desc(self.description)}</description>"
            f"<styleUrl>#{self.style_id}</styleUrl>"
            f"{self.geometry_xml}"
            "</Placemark>"
        )


def point_geometry(lon, lat):
    return f"<Point><coordinates>{lon:.6f},{lat:.6f},0</coordinates></Point>"


def polygon_geometry(rings):
    """rings: list of [(lon,lat), ...] ; first is outer, rest are holes."""
    outer = rings[0]
    coord_str = " ".join(f"{x:.6f},{y:.6f},0" for x, y in outer)
    xml = (
        "<Polygon><outerBoundaryIs><LinearRing><coordinates>"
        f"{coord_str}</coordinates></LinearRing></outerBoundaryIs>"
    )
    for hole in rings[1:]:
        hc = " ".join(f"{x:.6f},{y:.6f},0" for x, y in hole)
        xml += f"<innerBoundaryIs><LinearRing><coordinates>{hc}</coordinates></LinearRing></innerBoundaryIs>"
    xml += "</Polygon>"
    return xml


class KmlFolder:
    def __init__(self, name):
        self.name = name
        self.placemarks = []

    def add(self, placemark):
        self.placemarks.append(placemark)

    def to_xml(self):
        body = "".join(p.to_xml() for p in self.placemarks)
        return f"<Folder><name>{escape(self.name)}</name>{body}</Folder>"

    def feature_count(self):
        return len(self.placemarks)


class KmlDocument:
    def __init__(self, name):
        self.name = name
        self.styles = []
        self.folders = []

    def add_style(self, style):
        self.styles.append(style)

    def add_folder(self, folder):
        self.folders.append(folder)

    def feature_count(self):
        return sum(f.feature_count() for f in self.folders)

    def to_xml(self):
        styles_xml = "".join(s.to_xml() for s in self.styles)
        folders_xml = "".join(f.to_xml() for f in self.folders)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<kml xmlns="http://www.opengis.net/kml/2.2">'
            f"<Document><name>{escape(self.name)}</name>"
            f"{styles_xml}{folders_xml}"
            "</Document></kml>"
        )

    def write(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_xml())
