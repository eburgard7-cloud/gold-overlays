"""TNM Access API: historical topographic map sheets covering a point."""
from gold_overlays.config import SOURCES
from gold_overlays.http import cached_get_json, cached_download

TNM_API = SOURCES["topo"]["url"]


def list_historical_topos(bbox, refresh=False):
    minlon, minlat, maxlon, maxlat = bbox
    bbox_str = f"{minlon},{minlat},{maxlon},{maxlat}"
    items = []
    offset = 0
    while True:
        data = cached_get_json(TNM_API, params={
            "datasets": "Historical Topographic Maps",
            "bbox": bbox_str,
            "max": 100,
            "offset": offset,
        }, refresh=refresh)
        batch = data.get("items", [])
        items.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
    out = []
    for it in items:
        out.append({
            "title": it.get("title"),
            "date": it.get("publicationDate"),
            "scale": it.get("extent"),
            "url": it.get("downloadURL"),
            "size_bytes": it.get("sizeInBytes"),
        })
    return out


def pick_oldest(items, scale_keyword):
    matching = [i for i in items if scale_keyword.lower() in (i["scale"] or "").lower()]
    matching = [i for i in matching if i.get("date")]
    if not matching:
        return None
    return sorted(matching, key=lambda i: i["date"])[0]


def download(item, dest_path, max_bytes=150 * 1024 * 1024, refresh=False):
    if item.get("size_bytes") and item["size_bytes"] > max_bytes:
        return False, "over size cap"
    cached_download(item["url"], dest_path, refresh=refresh)
    return True, "ok"
