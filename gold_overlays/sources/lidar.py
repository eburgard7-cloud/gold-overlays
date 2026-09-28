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


def make_hud_overlay_png(out_png, px_w, px_h, meters_per_px, title):
    """A transparent, page-sized PNG carrying a title bar (top), north arrow
    (top-right) and scale bar (bottom-left) -- composited onto the GeoPDF
    page via the PDF driver's EXTRA_IMAGES option (a plain, non-georeferenced
    page overlay: image (x,y) is the image's bottom-left corner in PDF
    points, and at the driver's default DPI=72 with no WRITE_USERUNIT,
    1 raster pixel == 1 PDF point, so a page-sized overlay lines up exactly
    with no extra coordinate math -- confirmed empirically against gdal 3.8's
    PDF driver before relying on it here).
    """
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGBA", (px_w, px_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font

    # Title bar (top)
    bar_h = 50
    d.rectangle([0, 0, px_w, bar_h], fill=(0, 0, 0, 170))
    d.text((16, 12), title, fill=(255, 255, 255, 255), font=font)

    # North arrow (top-right, below title bar)
    ax, ay = px_w - 70, bar_h + 20
    d.polygon([(ax, ay), (ax - 18, ay + 55), (ax, ay + 38), (ax + 18, ay + 55)],
              fill=(0, 0, 0, 200), outline=(255, 255, 255, 255))
    d.text((ax - 6, ay - 24), "N", fill=(0, 0, 0, 220), font=font_sm)

    # Scale bar (bottom-left): pick a "nice" round length in meters
    for candidate_m in (2000, 1000, 500, 250, 100, 50, 25, 10):
        bar_px = candidate_m / meters_per_px
        if bar_px <= px_w * 0.35:
            scale_m = candidate_m
            break
    else:
        scale_m = 10
        bar_px = scale_m / meters_per_px
    sx0, sy0 = 24, px_h - 46
    bar_px = int(bar_px)
    d.rectangle([sx0 - 6, sy0 - 6, sx0 + bar_px + 6, sy0 + 26], fill=(0, 0, 0, 150))
    d.line([(sx0, sy0 + 10), (sx0 + bar_px, sy0 + 10)], fill=(255, 255, 255, 255), width=4)
    d.line([(sx0, sy0), (sx0, sy0 + 20)], fill=(255, 255, 255, 255), width=4)
    d.line([(sx0 + bar_px, sy0), (sx0 + bar_px, sy0 + 20)], fill=(255, 255, 255, 255), width=4)
    d.text((sx0, sy0 - 24), f"{scale_m} m", fill=(255, 255, 255, 255), font=font_sm)

    img.save(out_png)
    return out_png


def make_geopdf(hillshade_tif, overlay_gpkg_or_none, out_pdf, layer_name="Overlay",
                 title=None, meters_per_px=1.0):
    """Wrap the hillshade GeoTIFF in a GDAL geospatial PDF, burning in:
      - a vector overlay (claim shape + nearby layer-4 history sites) as a
        real, selectable PDF layer (OGR_DATASOURCE), if overlay_gpkg_or_none
        is given and exists;
      - a scale bar, north arrow, and title (EXTRA_IMAGES page overlay PNG).
    """
    cmd = ["gdal_translate", "-of", "PDF", "-co", "COMPRESS=JPEG"]
    if overlay_gpkg_or_none and os.path.exists(overlay_gpkg_or_none):
        cmd += [
            "-co", f"OGR_DATASOURCE={overlay_gpkg_or_none}",
            "-co", f"EXTRA_LAYER_NAME={layer_name}",
            "-co", "OGR_DISPLAY_FIELD=name",
        ]
    hud_png = None
    try:
        import subprocess as _sp
        info = _sp.run(["gdalinfo", "-json", hillshade_tif], capture_output=True, check=True)
        import json as _json
        size = _json.loads(info.stdout)["size"]
        px_w, px_h = size[0], size[1]
        hud_png = out_pdf + ".hud.png"
        make_hud_overlay_png(hud_png, px_w, px_h, meters_per_px, title or layer_name)
        cmd += ["-co", f"EXTRA_IMAGES={hud_png},0,0,1"]
    except Exception:
        hud_png = None
    cmd += [hillshade_tif, out_pdf]
    r = subprocess.run(cmd, capture_output=True)
    if hud_png and os.path.exists(hud_png):
        os.remove(hud_png)
    return r.returncode == 0
