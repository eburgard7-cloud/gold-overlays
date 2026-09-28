#!/usr/bin/env python3
"""Re-pull layer C (BLM MLRS active claims, Not Closed) for every area and
report what's new or closed since the last run.

Intended to be run monthly (per the user's plan). Always hits the network
(refresh=True) since the whole point is to see what changed.

Writes:
  out/claims_snapshot.json   current full snapshot (serial -> claim dict), used as "last run" next time
  out/claims_changes.md      human-readable diff against the previous snapshot
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gold_overlays.config import AREAS
from gold_overlays.sources import blm_claims

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
SNAPSHOT_PATH = os.path.join(OUT_DIR, "claims_snapshot.json")
CHANGES_PATH = os.path.join(OUT_DIR, "claims_changes.md")


def claim_key(c):
    return c.get("legacy_serial") or c.get("serial")


def fetch_all_active():
    combined = {}
    for area, bbox in AREAS.items():
        claims = blm_claims.fetch_active(bbox, refresh=True)
        for c in claims:
            key = claim_key(c)
            if not key:
                continue
            c["_area"] = area
            combined[key] = c
    return combined


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    previous = {}
    if os.path.exists(SNAPSHOT_PATH):
        with open(SNAPSHOT_PATH) as f:
            previous = json.load(f)

    current = fetch_all_active()

    new_serials = sorted(set(current) - set(previous))
    closed_serials = sorted(set(previous) - set(current))
    changed_fields = []
    for k in sorted(set(current) & set(previous)):
        a, b = previous[k], current[k]
        if a.get("disposition") != b.get("disposition") or a.get("acres") != b.get("acres"):
            changed_fields.append((k, a, b))

    today = datetime.date.today().isoformat()
    lines = [f"# Claims change report -- {today}", ""]
    lines.append(f"Compared {len(previous)} previously-seen active claims against {len(current)} now returned "
                 f"by BLM MLRS Not Closed across all {len(AREAS)} areas.")
    lines.append("")
    lines.append(f"## New active claims ({len(new_serials)})")
    for k in new_serials:
        c = current[k]
        lines.append(f"- **{c['name']}** ({k}) -- {c['case_type']}, {c['acres']} ac, area: {c['_area']}")
    lines.append("")
    lines.append(f"## No longer in 'Not Closed' (closed/relinquished/expired since last run) ({len(closed_serials)})")
    for k in closed_serials:
        c = previous[k]
        lines.append(f"- **{c['name']}** ({k}) -- last seen {c['case_type']}, {c['acres']} ac, area: {c.get('_area')}")
    lines.append("")
    lines.append(f"## Changed disposition/acreage ({len(changed_fields)})")
    for k, a, b in changed_fields:
        lines.append(f"- **{b['name']}** ({k}): {a.get('disposition')}/{a.get('acres')}ac -> {b.get('disposition')}/{b.get('acres')}ac")
    lines.append("")

    with open(CHANGES_PATH, "w") as f:
        f.write("\n".join(lines))
    with open(SNAPSHOT_PATH, "w") as f:
        json.dump(current, f, indent=2, default=str)

    print(f"Wrote {CHANGES_PATH} ({len(new_serials)} new, {len(closed_serials)} closed, {len(changed_fields)} changed)")


if __name__ == "__main__":
    main()
