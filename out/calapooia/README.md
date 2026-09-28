# calapooia -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-122.55, 44.15, -122.28, 44.32)`
Built: 2026-09-28

## Output files
- `calapooia_onx.kml` / `calapooia_onx.gpx` -- 343 features, 106 KB KML / 83 KB GPX
  - layers: My claims & public sites, Historical workings (USMIN), Mine & prospect sites (MILO/MRDS, gold), Active mining claims (BLM MLRS), Open ground to sample

## Layer counts
- My claims & public sites: 1
- USMIN historical workings: 17 (dropped types: borrow pit, open pit mine or quarry, quarry)
- MILO-4 gold sites: 272
- MRDS gold sites (raw / kept after MILO dedup): 15 / 7
- Active BLM claims (Not Closed): 21
- Closed placer claims fetched: 3 (unmatched to any 500m hex: 0)
- Land status polygons fetched: BLM=1, USFS=1
- NHD service reachable for this area: True
- Open ground to sample: 25 waypoints

## My claims & public sites (reference table)
- **Golden Dollar** -- polygon (GOLDEN DOLLAR)

## Past claim density -- top cells

| lat | lon | total closed placer claims | by decade |
|---|---|---|---|

## Open ground to sample -- top 10

| waypoint | lat | lon | feature type | near active claim |
|---|---|---|---|---|
| OPEN-calapooia-01 | 44.23027 | -122.33201 | placer (heuristic: surface workings) | False |
| OPEN-calapooia-02 | 44.22626 | -122.33845 | Adit | False |
| OPEN-calapooia-03 | 44.22455 | -122.35387 | Adit | False |
| OPEN-calapooia-04 | 44.20581 | -122.37208 | Adit | False |
| OPEN-calapooia-05 | 44.22885 | -122.34564 | lode | False |
| OPEN-calapooia-06 | 44.22880 | -122.34552 | lode | False |
| OPEN-calapooia-07 | 44.22746 | -122.34444 | lode | False |
| OPEN-calapooia-08 | 44.22803 | -122.34381 | lode | False |
| OPEN-calapooia-09 | 44.22930 | -122.33016 | lode | False |
| OPEN-calapooia-10 | 44.23027 | -122.33200 | Open Pit Mine | False |

## Caveats specific to this area
- BLM claim polygons are approximate to the quarter-section; every claim polygon is labeled
  `[APPROX quarter-section]` in its name and description.
- 'Closed-claim density' decade buckets use the MLRS `Created` (database record) date as a proxy for
  located date -- the public feature service does not expose a true located/last-action date.
- 'Open ground' ranking's final tiebreaker is distance-to-stream, not distance-to-road (no road
  dataset was fetched in this build).
- MRDS attribute detail is limited to what its public WFS exposes (name/status/commodity codes);
  full deposit-type/production detail lives on the per-site page linked in each description.

## DOGAMI Bulletin 61 notes


**Blue River district** (Bulletin 61 p. 299-306; southern Linn / northern Lane
County, Ts. 15-16 S., R. 4 E., straddling the Calapooia/McKenzie drainage divide).
Bulletin 61 does not have a separate "Calapooia" district -- the upper Calapooia
River headwaters fall within the area the bulletin treats as the Blue River
district. Principal mine: **Lucky Boy** (reached via a road up Quartz Creek from
the town of Blue River), with lesser prospects Cinderella, Great Northern, Poorman,
Rowena, Tate, Treasurer, Union. Veins carry pyrite/sphalerite/galena/chalcopyrite in
a quartz gangue, with calcite locally dominant (Great Northern, Higgins, Cinderella).
Western Cascades total production (combining Blue River + Fall Creek + other minor
districts, not separated out) is given as **about $1.5 million** (p. 306, 15373 in
the OCR text).

**Caveat:** no placer-specific content or named bars/benches for the Calapooia River
itself were found in Bulletin 61 -- treat this area's placer potential as inferred
from lode erosion, not from any documented placer history.

**OHMI (Linn County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-linn.aspx

