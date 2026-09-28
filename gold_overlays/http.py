"""Small HTTP helpers: caching GET/download, ArcGIS pagination."""
import hashlib
import json
import os
import time

import requests

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "gold-overlays-build/1.0 (personal prospecting overlays)"})


def _cache_key(url, params):
    raw = url + "?" + json.dumps(params or {}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def cached_get_json(url, params=None, refresh=False, retries=3, timeout=60):
    key = _cache_key(url, params)
    path = os.path.join(CACHE_DIR, key + ".json")
    if not refresh and os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    last_err = None
    for attempt in range(retries):
        try:
            r = SESSION.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            with open(path, "w") as f:
                json.dump(data, f)
            return data
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} tries: {url} params={params}: {last_err}")


def cached_download(url, dest_path, refresh=False, timeout=120):
    if not refresh and os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return dest_path
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    r = SESSION.get(url, timeout=timeout, stream=True)
    r.raise_for_status()
    tmp = dest_path + ".part"
    with open(tmp, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 16):
            f.write(chunk)
    os.replace(tmp, dest_path)
    return dest_path


def arcgis_query_all(url, where="1=1", geometry=None, geometry_type="esriGeometryEnvelope",
                      in_sr=4326, out_sr=4326, out_fields="*", extra_params=None,
                      page_size=2000, refresh=False, return_geometry=True):
    """Paginate an ArcGIS FeatureServer/MapServer /query endpoint by resultOffset."""
    features = []
    offset = 0
    while True:
        params = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": str(return_geometry).lower(),
            "outSR": out_sr,
            "f": "json",
            "resultRecordCount": page_size,
            "resultOffset": offset,
        }
        if geometry is not None:
            params.update({
                "geometry": geometry,
                "geometryType": geometry_type,
                "inSR": in_sr,
                "spatialRel": "esriSpatialRelIntersects",
            })
        if extra_params:
            params.update(extra_params)
        data = cached_get_json(url + "/query", params, refresh=refresh)
        if "error" in data:
            raise RuntimeError(f"ArcGIS query error: {data['error']}")
        feats = data.get("features", [])
        features.extend(feats)
        if len(feats) < page_size:
            break
        offset += page_size
    return features
