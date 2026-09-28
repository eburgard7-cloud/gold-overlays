"""ogr2ogr wrapper with retries -- the mrdata.usgs.gov WFS mapserver
intermittently returns HTTP 502 (observed on the quartzville bbox for
usmin points) with no relation to result size; a plain retry-with-backoff
clears it in practice.
"""
import subprocess
import time


def run_ogr2ogr(args, retries=4, timeout=120):
    last_exc = None
    for attempt in range(retries):
        try:
            return subprocess.run(args, check=True, capture_output=True, timeout=timeout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            last_exc = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"ogr2ogr failed after {retries} attempts: {args}: {last_exc}")
