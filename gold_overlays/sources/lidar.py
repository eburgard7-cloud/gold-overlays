"""DOGAMI bare-earth lidar hillshade export (ImageServer/exportImage) + GeoPDF via GDAL."""
import math
import os
import subprocess

from gold_overlays.config import SOURCES
from gold_overlays.http import SESSION

IMAGE_SERVER = SOURCES["lidar"]["url"]


def bbox_2km_around(lon, lat, size_m=2000):
    dlat = size_m / 2.0 / 111320.0
    dlon = size_m / 2.0 / (111320.0 * max(math.cos(math.radians(lat)), 0.1))
    return (lon - dlon, lat - dlat, lon + dlon, lat + dlat)


def export_hillshade_tif(lon, lat, out_tif, size_m=2000, px=2000, timeout=120):
    """Export a ~size_m x size_m bare-earth hillshade GeoTIFF centered on lon/lat.
    Returns True on success, False if the service refuses/errors.
    """
    minlon, minlat, maxlon, maxlat = bbox_2km_around(lon, lat, size_m)
    params = {
        "bbox": f"{minlon},{minlat},{maxlon},{maxlat}",
        "bboxSR": 4326,
        "imageSR": 4326,
        "size": f"{px},{px}",
        "format": "tiff",
        "interpolation": "RSP_BilinearInterpolation",
        "f": "image",
    }
    try:
        r = SESSION.get(IMAGE_SERVER + "/exportImage", params=params, timeout=timeout)
        r.raise_for_status()
        if r.headers.get("Content-Type", "").startswith("application/json"):
            return False  # server returned an error payload instead of an image
        raw_tif = out_tif + ".raw.tif"
        with open(raw_tif, "wb") as f:
            f.write(r.content)
        # Re-compress with DEFLATE to keep file size down for git.
        subprocess.run(
            ["gdal_translate", "-co", "COMPRESS=DEFLATE", "-co", "PREDICTOR=2", raw_tif, out_tif],
            check=True, capture_output=True,
        )
        os.remove(raw_tif)
        return True
    except Exception:
        return False


def make_geopdf(hillshade_tif, overlay_gpkg_or_none, out_pdf, layer_name="Overlay"):
    """Wrap the hillshade GeoTIFF in a GDAL geospatial PDF, optionally burning
    in a vector overlay (claim outline / point) as a real (selectable) PDF layer.
    """
    cmd = ["gdal_translate", "-of", "PDF", "-co", "COMPRESS=JPEG"]
    if overlay_gpkg_or_none and os.path.exists(overlay_gpkg_or_none):
        cmd += [
            "-co", f"OGR_DATASOURCE={overlay_gpkg_or_none}",
            "-co", f"EXTRA_LAYER_NAME={layer_name}",
        ]
    cmd += [hillshade_tif, out_pdf]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0
