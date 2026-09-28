"""Geometry helpers built on shapely/pyproj."""
import math

from pyproj import Transformer
from shapely.geometry import Polygon, MultiPolygon, Point, shape as shp_shape
from shapely.ops import unary_union

_TRANSFORMERS = {}


def to_wgs84(geom, from_epsg):
    """Reproject a shapely geometry from from_epsg to EPSG:4326."""
    if from_epsg == 4326:
        return geom
    key = from_epsg
    if key not in _TRANSFORMERS:
        _TRANSFORMERS[key] = Transformer.from_crs(f"EPSG:{from_epsg}", "EPSG:4326", always_xy=True)
    t = _TRANSFORMERS[key]
    from shapely.ops import transform
    return transform(lambda x, y, z=None: t.transform(x, y), geom)


def esri_rings_to_polygon(rings):
    """esriJSON polygon rings -> shapely Polygon/MultiPolygon.

    Esri encodes exterior rings clockwise and holes counter-clockwise; we
    don't rely on winding, we just bucket by signed area. Rather than
    manually pairing each hole with its enclosing exterior (O(exteriors *
    holes) point-in-polygon tests -- painfully slow for a BLM/USFS land
    layer that can return a single multi-thousand-ring feature), we build
    the union of exteriors and subtract the union of holes: algebraically
    identical for well-formed esri polygons, and GEOS's union/difference
    are index-accelerated instead of brute-force.
    """
    def ring_area(r):
        a = 0.0
        for i in range(len(r) - 1):
            x1, y1 = r[i]
            x2, y2 = r[i + 1]
            a += x1 * y2 - x2 * y1
        return a / 2.0

    exteriors = []
    holes = []
    for r in rings:
        if len(r) < 4:
            continue
        if ring_area(r) < 0:  # clockwise = exterior (esri convention)
            exteriors.append(r)
        else:
            holes.append(r)
    if not exteriors:
        exteriors = rings
        holes = []

    def _safe_polys(ring_list):
        polys = []
        for r in ring_list:
            p = Polygon(r)
            if not p.is_valid:
                p = p.buffer(0)
            polys.append(p)
        return polys

    ext_union = unary_union(_safe_polys(exteriors))
    if holes:
        hole_union = unary_union(_safe_polys(holes))
        result = ext_union.difference(hole_union)
    else:
        result = ext_union
    if not result.is_valid:
        result = result.buffer(0)
    return result


def esri_paths_to_lines(paths):
    from shapely.geometry import MultiLineString
    return MultiLineString([p for p in paths if len(p) >= 2])


def meters_to_deg_lat(m):
    return m / 111320.0


def meters_to_deg_lon(m, lat):
    return m / (111320.0 * max(math.cos(math.radians(lat)), 0.1))


def point_distance_m(lon1, lat1, lon2, lat2):
    """Fast equirectangular-approx distance in meters (fine at these scales)."""
    lat0 = (lat1 + lat2) / 2.0
    dx = (lon1 - lon2) * 111320.0 * max(math.cos(math.radians(lat0)), 0.1)
    dy = (lat1 - lat2) * 111320.0
    return math.hypot(dx, dy)


def bbox_center(bbox):
    minlon, minlat, maxlon, maxlat = bbox
    return ((minlon + maxlon) / 2.0, (minlat + maxlat) / 2.0)


def make_hex_grid(bbox, cell_size_m=500):
    """Flat-top hex grid covering bbox. Returns list of shapely Polygons (lon/lat)."""
    minlon, minlat, maxlon, maxlat = bbox
    lat0 = (minlat + maxlat) / 2.0
    dx = meters_to_deg_lon(cell_size_m * 1.5, lat0)
    dy = meters_to_deg_lat(cell_size_m * math.sqrt(3))
    r = meters_to_deg_lon(cell_size_m, lat0)
    r_y = meters_to_deg_lat(cell_size_m)

    hexes = []
    col = 0
    x = minlon - dx
    while x < maxlon + dx:
        y_offset = (dy / 2.0) if (col % 2) else 0.0
        y = minlat - dy + y_offset
        while y < maxlat + dy:
            cx, cy = x, y
            pts = []
            for k in range(6):
                ang = math.radians(60 * k)
                pts.append((cx + r * math.cos(ang), cy + r_y * math.sin(ang)))
            hexes.append(Polygon(pts))
            y += dy
        x += dx
        col += 1
    return hexes


class LocalProjector:
    """Cheap equirectangular projection (meters) local to a bbox, built once
    and reused for every geometry -- avoids the O(features) reprojection
    cost of calling shapely.ops.transform per distance query.
    """

    def __init__(self, bbox):
        minlon, minlat, maxlon, maxlat = bbox
        self.lon0 = (minlon + maxlon) / 2.0
        self.lat0 = (minlat + maxlat) / 2.0
        self.m_per_deg_lat = 111320.0
        self.m_per_deg_lon = 111320.0 * max(math.cos(math.radians(self.lat0)), 0.1)

    def to_local(self, geom):
        from shapely.ops import transform
        return transform(
            lambda x, y, z=None: ((x - self.lon0) * self.m_per_deg_lon, (y - self.lat0) * self.m_per_deg_lat),
            geom,
        )

    def point_to_local(self, lon, lat):
        return Point((lon - self.lon0) * self.m_per_deg_lon, (lat - self.lat0) * self.m_per_deg_lat)


def polygon_to_rings(geom):
    """shapely Polygon -> [exterior, hole1, hole2, ...] as (x,y) tuple lists,
    for kml_writer.polygon_geometry / gpx_writer.GpxTrack.
    """
    exterior = list(geom.exterior.coords)
    holes = [list(interior.coords) for interior in geom.interiors]
    return [exterior] + holes


def clip_rings_to_bbox(rings, bbox, prefer_point=None):
    """esriJSON-style rings -> ring-lists clipped to bbox, largest part only.

    Source claim/feature data (BLM MLRS in particular) occasionally has a
    ring belonging to a completely different, far-away parcel bundled into
    the same feature's ring list (a PLSS-aliquot matching error in the
    source, evidenced by its own QLTY/data-quality field). Naively treating
    ring[1:] as holes of ring[0] (as raw esriJSON would suggest) then draws
    that stray ring as a "donut hole" tens of km from the real claim.
    Clipping to the query bbox and keeping only the largest resulting part
    both fixes that misrender and directly enforces "no feature falls
    outside its area's bounding box".　Returns (rings_or_None, was_clipped).
    """
    from shapely.geometry import box as shp_box
    poly = esri_rings_to_polygon(rings)
    bbox_poly = shp_box(*bbox)
    if poly.is_empty:
        return None, False
    clipped = poly.intersection(bbox_poly)
    if clipped.is_empty:
        return None, True
    was_clipped = clipped.area < poly.area * 0.999
    if clipped.geom_type == "MultiPolygon":
        was_clipped = True
        chosen = None
        if prefer_point is not None:
            for part in clipped.geoms:
                if part.contains(Point(prefer_point)):
                    chosen = part
                    break
        clipped = chosen if chosen is not None else max(clipped.geoms, key=lambda g: g.area)
    elif clipped.geom_type != "Polygon":
        return None, True
    return polygon_to_rings(clipped), was_clipped


def point_within_any(point, polygons):
    for poly in polygons:
        if poly.contains(point) or poly.touches(point):
            return True
    return False


def min_distance_m(point_lonlat, geoms):
    """Approximate min great-circle-ish distance in meters from a point to a list of shapely geoms (lon/lat)."""
    if not geoms:
        return None
    lon, lat = point_lonlat.x, point_lonlat.y
    m_per_deg_lat = 111320.0
    m_per_deg_lon = 111320.0 * max(math.cos(math.radians(lat)), 0.1)

    def scale(geom):
        from shapely.ops import transform
        return transform(lambda x, y, z=None: ((x - lon) * m_per_deg_lon, (y - lat) * m_per_deg_lat), geom)

    origin = Point(0, 0)
    best = None
    for g in geoms:
        try:
            d = origin.distance(scale(g))
        except Exception:
            continue
        if best is None or d < best:
            best = d
    return best
