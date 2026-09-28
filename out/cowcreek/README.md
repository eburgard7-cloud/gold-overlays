# cowcreek -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-123.7, 42.68, -123.1, 42.98)`
Built: 2026-09-28

## Output files
- `cowcreek_onx.kml` / `cowcreek_onx.gpx` -- 692 features, 360 KB KML / 436 KB GPX
  - layers: My claims & public sites, Historical workings (USMIN), Mine & prospect sites (MILO/MRDS, gold), Active mining claims (BLM MLRS), Past claim density (closed placer, 500m hex), Open ground to sample

## Layer counts
- My claims & public sites: 5
- USMIN historical workings: 225 (dropped types: borrow pit, gravel pit, open pit mine or quarry, quarry)
- MILO-4 gold sites: 167
- MRDS gold sites (raw / kept after MILO dedup): 113 / 38
- Active BLM claims (Not Closed): 207
- Closed placer claims fetched: 269 (unmatched to any 500m hex: 4)
- Land status polygons fetched: BLM=1, USFS=0
- NHD service reachable for this area: True
- Open ground to sample: 25 waypoints

## My claims & public sites (reference table)
- **WVM #3 Dads Creek** -- polygon (WVM #3)
- **WVM #4 Dads Creek** -- polygon (WVM #4)
- **WVM #5 Dads Creek** -- polygon (WVM #5)
- **Pure White Gold (Whitehorse Cr)** -- polygon (PURE WHITE GOLD)
- **Cow Creek Recreational Gold Panning Area** -- point (published site)

## Past claim density -- top cells

| lat | lon | total closed placer claims | by decade |
|---|---|---|---|
| 42.9056 | -123.5255 | 26 | 2020s:26 |
| 42.9095 | -123.4795 | 26 | 2020s:26 |
| 42.9756 | -123.4152 | 14 | 2020s:14 |
| 42.9328 | -123.4795 | 13 | 2020s:13 |
| 42.8939 | -123.4979 | 11 | 2020s:11 |
| 42.9095 | -123.5530 | 10 | 2020s:10 |
| 42.9834 | -123.3785 | 10 | 2020s:10 |
| 42.9134 | -123.5438 | 8 | 2020s:8 |
| 42.9251 | -123.5346 | 8 | 2020s:8 |
| 42.9095 | -123.5163 | 8 | 2020s:8 |

## Open ground to sample -- top 10

| waypoint | lat | lon | feature type | near active claim |
|---|---|---|---|---|
| OPEN-cowcreek-01 | 42.71624 | -123.25758 | placer (heuristic: surface workings) | False |
| OPEN-cowcreek-02 | 42.86218 | -123.38588 | Prospect Pit | False |
| OPEN-cowcreek-03 | 42.69800 | -123.60840 | Prospect Pit | False |
| OPEN-cowcreek-04 | 42.69928 | -123.60877 | Prospect Pit | False |
| OPEN-cowcreek-05 | 42.69838 | -123.60798 | Adit | False |
| OPEN-cowcreek-06 | 42.69712 | -123.60911 | Adit | False |
| OPEN-cowcreek-07 | 42.69794 | -123.60989 | Prospect Pit | False |
| OPEN-cowcreek-08 | 42.71329 | -123.57745 | Adit | False |
| OPEN-cowcreek-09 | 42.71402 | -123.57706 | Adit | False |
| OPEN-cowcreek-10 | 42.86257 | -123.38471 | Prospect Pit | False |

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


**Silver Peak area** (Bulletin 61 p. 213-214; Douglas County, southwest of
Canyonville, T. 31 S., Rs. 5-6 W., draining to Cow Creek and the South Umpqua).
Lode total for the area is estimated at **about $216,000** prior to 1930 (Silver
Peak mine ~$73,000 of shipped ore 1922-1930; Gold Bluff mine $7,000-$40,000+ across
several owners; Levens Ledge $75,000-$80,000).

**Placer mining** (p. 214, directly relevant to the Cow Creek byway area): "Some
evidence of placer mining can be found on Jordan, Mitchell, Russell, and West Fork
Canyon Creeks and on Middle Creek... but no records of this activity have been
published." **"The most extensive placer-mining operations were in bench gravels
along Cow Creek southwest of this area. Of these, the Victory placer in sec. 33,
T. 32 S., R. 7 W. (about 6 miles west of Glendale) was probably the largest
producer"** -- squarely inside this build's Cow Creek byway box. Diller & Kay
(1924) also describe placer workings on Quaternary bench gravels ~500 ft above
present streams between Riddle and Canyonville, with gold partly derived from
decomposition of the underlying Cretaceous (Riddle Fm) sediments.

Dads Creek and Whitehorse Creek (both hosting WVM claims in the reference table)
are not individually named in Bulletin 61; treat their placer potential as
consistent with the broader Cow Creek bench-gravel pattern documented above.

**OHMI (Douglas County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-douglas.aspx

