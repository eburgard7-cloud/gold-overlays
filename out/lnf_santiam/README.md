# lnf_santiam -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-122.62, 44.75, -122.4, 44.86)`
Built: 2026-09-28

## Output files
- `lnf_santiam_onx.kml` / `lnf_santiam_onx.gpx` -- 6 features, 6 KB KML / 5 KB GPX
  - layers: My claims & public sites, Active mining claims (BLM MLRS)

## Layer counts
- My claims & public sites: 1
- USMIN historical workings: 0 (dropped types: borrow pit, gravel pit, quarry)
- MILO-4 gold sites: 0
- MRDS gold sites (raw / kept after MILO dedup): 0 / 0
- Active BLM claims (Not Closed): 5
- Closed placer claims fetched: 2 (unmatched to any 500m hex: 0)
- Land status polygons fetched: BLM=1, USFS=0
- NHD service reachable for this area: True
- Open ground to sample: 0 waypoints

## My claims & public sites (reference table)
- **WVM-LNF25 Little North Santiam** -- point (no MLRS polygon available yet)

## Past claim density -- top cells

| lat | lon | total closed placer claims | by decade |
|---|---|---|---|

## Open ground to sample -- top 10

| waypoint | lat | lon | feature type | near active claim |
|---|---|---|---|---|

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


**North Santiam district** (Bulletin 61 p. 286-289; Clackamas/Marion Counties,
T. 8 S., Rs. 4-5 E., along the Little North Santiam River). Mineralization
discovered about 1877; most properties located by 1903. District total recorded
production 1896-1947 is **about $25,000** (454 oz gold, 1,412 oz silver, plus
copper/lead/zinc byproduct). Documented zoning from a high-temperature
chalcopyrite-bearing core (Crown mine, along the river) outward through
pyrite-bearing veins (Gold Creek) to complex sulfide veins (Blende Oro, Ruth) to a
low-temperature calcite-vein outer zone (lower Elkhorn Creek, Ogle Mountain mine).
Most-developed mines: Ogle Mountain (~$10,000, worked 1903-1919), Ruth
(zinc-focused, >4,000 ft of workings), Santiam Copper (shipped ore/concentrate
1923-1940, averaging ~10% Cu, 3 oz/ton Ag, 0.03 oz/ton Au).

**Caveat:** again lode-focused; no named placer bars on the Little North Santiam
itself are given, though the district's many creek-adjacent lode workings (Gold
Creek, Elkhorn Creek) are consistent with the placer colors panners find today.

**OHMI (Marion County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-marion.aspx -- **(Clackamas County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-clackamas.aspx

