# quartzville -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-122.5, 44.48, -122.15, 44.68)`
Built: 2026-09-28

## Output files
- `quartzville_onx.kml` / `quartzville_onx.gpx` -- 293 features, 112 KB KML / 106 KB GPX
  - layers: My claims & public sites, Historical workings (USMIN), Mine & prospect sites (MILO/MRDS, gold), Active mining claims (BLM MLRS), Open ground to sample

## Layer counts
- My claims & public sites: 2
- USMIN historical workings: 22 (dropped types: borrow pit, gravel pit, quarry)
- MILO-4 gold sites: 185
- MRDS gold sites (raw / kept after MILO dedup): 16 / 9
- Active BLM claims (Not Closed): 50
- Closed placer claims fetched: 1 (unmatched to any 500m hex: 0)
- Land status polygons fetched: BLM=1, USFS=1
- NHD service reachable for this area: True
- Open ground to sample: 25 waypoints

## My claims & public sites (reference table)
- **WVM #1B Dry Gulch** -- polygon (WVM #1  B)
- **Cedar Bend Placer** -- polygon (CEDAR BEND)

## Past claim density -- top cells

| lat | lon | total closed placer claims | by decade |
|---|---|---|---|

## Open ground to sample -- top 10

| waypoint | lat | lon | feature type | near active claim |
|---|---|---|---|---|
| OPEN-quartzville-01 | 44.55486 | -122.27591 | placer (heuristic: surface workings) | False |
| OPEN-quartzville-02 | 44.54771 | -122.27501 | Prospect Pit | False |
| OPEN-quartzville-03 | 44.57263 | -122.29176 | Prospect Pit | False |
| OPEN-quartzville-04 | 44.54663 | -122.25809 | Prospect Pit | False |
| OPEN-quartzville-05 | 44.58234 | -122.31155 | Prospect Pit | False |
| OPEN-quartzville-06 | 44.59715 | -122.32157 | unknown | False |
| OPEN-quartzville-07 | 44.59764 | -122.32172 | unknown | False |
| OPEN-quartzville-08 | 44.59827 | -122.32139 | unknown | False |
| OPEN-quartzville-09 | 44.59801 | -122.32165 | unknown | False |
| OPEN-quartzville-10 | 44.60021 | -122.31927 | unknown | False |

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


**Quartzville district** (Bulletin 61 p. 295-298; Linn County, mainly T. 11-12 S., R. 4 E.).
One of the five main Western Cascades mineralized districts. Documented mines/claims:
Galena, Lawler, Lucille (Snowstorm & Bell), Munro (Mayflower), Paymaster, Red Heifer
(Silver Signal), Riverside, Savage (Vandalia/Golden West), Tillicum & Cumtillie
(Golden Fleece). First discovery in the district reported 1861 (Lawler mine); the
Lawler is the best-documented producer at **about $100,000** (ground in a 20-stamp
mill, shut down 1898). Munro group owner reported 72.56 oz gold. Savage/Vandalia +
Golden West combined 1921 production about $7,000.

**Caveat:** like Bohemia, this section is lode-focused (quartz veins, shear zones in
andesite/tuff/rhyolite); it does not name placer bars on Quartzville Creek, Canal
Creek, or Dry Gulch specifically. Placer gold reaching these creeks is consistent
with erosion of the many small lode prospects listed above, upstream of Green Peter
Reservoir.

**OHMI (Linn County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-linn.aspx

