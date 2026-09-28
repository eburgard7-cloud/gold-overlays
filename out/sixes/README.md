# sixes -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-124.45, 42.75, -124.2, 42.88)`
Built: 2026-09-28

## Output files
- `sixes_onx.kml` / `sixes_onx.gpx` -- 71 features, 35 KB KML / 34 KB GPX
  - layers: My claims & public sites, Historical workings (USMIN), Mine & prospect sites (MILO/MRDS, gold), Active mining claims (BLM MLRS), Open ground to sample

## Layer counts
- My claims & public sites: 1
- USMIN historical workings: 5 (dropped types: borrow pit, gravel pit, open pit mine or quarry, quarry)
- MILO-4 gold sites: 19
- MRDS gold sites (raw / kept after MILO dedup): 16 / 6
- Active BLM claims (Not Closed): 34
- Closed placer claims fetched: 3 (unmatched to any 500m hex: 0)
- Land status polygons fetched: BLM=1, USFS=1
- NHD service reachable for this area: True
- Open ground to sample: 6 waypoints

## My claims & public sites (reference table)
- **Sixes River Campground (rec mining)** -- point (published site)

## Past claim density -- top cells

| lat | lon | total closed placer claims | by decade |
|---|---|---|---|

## Open ground to sample -- top 10

| waypoint | lat | lon | feature type | near active claim |
|---|---|---|---|---|
| OPEN-sixes-01 | 42.80451 | -124.30431 | placer (heuristic: surface workings) | False |
| OPEN-sixes-02 | 42.77624 | -124.24683 | placer | True |
| OPEN-sixes-03 | 42.76874 | -124.24563 | placer | False |
| OPEN-sixes-04 | 42.80400 | -124.31790 | placer | False |
| OPEN-sixes-05 | 42.80453 | -124.30406 | Open Pit Mine | False |
| OPEN-sixes-06 | 42.77704 | -124.20812 | lode | False |

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


**Salmon Mountain-Sixes area** (Bulletin 61 p. 182-183; southern Coos / northern
Curry County, Ts. 32-33 S., Rs. 12-14 W., between the Sixes and Elk Rivers). Diller
(1903) called it the "gold belt of the Port Orford quadrangle" and it "has long been
the most active mining region of the Oregon coast" -- **total production from the
quadrangle since 1852 is estimated at about $1,000,000**, almost entirely from
PLACER, not lode: "Nearly all of the gold which has thus far been obtained... has
come from placer mines, some of which are along beaches... and the rest in river
gravels, especially **along the South Fork of the Sixes** and at the heads of Salmon
and Johnson Creeks" (p. 182-183, quoting Diller 1903).

**Named productive creeks / bars:** Johnson Creek placers (most successful near its
head, close to the dacite-porphyry belt; landslides in spring 1890 buried the
streambed and ended profitable mining; the "Big Slide" placer near NE sec. 34,
T. 32 S., R. 12 W. was later worked seasonally). **"Numerous placer operations were
active along the South Fork of Sixes River during the late 1800's. Many of these
worked bench gravels from about 50 feet to as much as 130 feet above the present
stream."** Very little mining occurred on the Sixes mainstem above the South Fork
mouth (p. 183).

**OHMI (Curry County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-curry.aspx -- **(Coos County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-coos.aspx

