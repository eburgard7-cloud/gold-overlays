# bohemia -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-122.95, 43.45, -122.5, 43.78)`
Built: 2026-09-28

## Output files
- `bohemia_onx.kml` / `bohemia_onx.gpx` -- 1364 features, 436 KB KML / 367 KB GPX
  - layers: My claims & public sites, Historical workings (USMIN), Mine & prospect sites (MILO/MRDS, gold), Active mining claims (BLM MLRS), Open ground to sample

## Layer counts
- My claims & public sites: 10
- USMIN historical workings: 64 (dropped types: borrow pit, open pit mine or quarry, quarry)
- MILO-4 gold sites: 1067
- MRDS gold sites (raw / kept after MILO dedup): 77 / 51
- Active BLM claims (Not Closed): 147
- Closed placer claims fetched: 8 (unmatched to any 500m hex: 0)
- Land status polygons fetched: BLM=1, USFS=1
- NHD service reachable for this area: True
- Open ground to sample: 25 waypoints

## My claims & public sites (reference table)
- **BMOA War Eagle III** -- polygon (WAR EAGLE III)
- **BMOA Westside** -- polygon (WESTSIDE)
- **BMOA Y Not** -- polygon (Y NOT)
- **BMOA Placer Claim** -- polygon (PLACER CLAIM)
- **BMOA Little Red** -- polygon (LITTLE RED)
- **BMOA Big Bend** -- polygon (BIG BEND)
- **BMOA Argentite** -- polygon (ARGENTITE)
- **BMOA Exodus** -- polygon (EXODUS)
- **BMOA 4 Aces** -- polygon (4 ACES)
- **Cedar Creek Campground (Brice Cr)** -- point (published site)

## Past claim density -- top cells

| lat | lon | total closed placer claims | by decade |
|---|---|---|---|

## Open ground to sample -- top 10

| waypoint | lat | lon | feature type | near active claim |
|---|---|---|---|---|
| OPEN-bohemia-01 | 43.59779 | -122.65981 | placer (heuristic: surface workings) | False |
| OPEN-bohemia-02 | 43.59784 | -122.75227 | placer (heuristic: surface workings) | False |
| OPEN-bohemia-03 | 43.59760 | -122.75248 | placer (heuristic: surface workings) | False |
| OPEN-bohemia-04 | 43.59736 | -122.75232 | placer (heuristic: surface workings) | False |
| OPEN-bohemia-05 | 43.59745 | -122.75232 | placer (heuristic: surface workings) | False |
| OPEN-bohemia-06 | 43.60098 | -122.66108 | placer (heuristic: surface workings) | False |
| OPEN-bohemia-07 | 43.55954 | -122.60054 | placer (heuristic: surface workings) | False |
| OPEN-bohemia-08 | 43.50547 | -122.83965 | placer (heuristic: surface workings) | False |
| OPEN-bohemia-09 | 43.56791 | -122.59304 | Adit | False |
| OPEN-bohemia-10 | 43.59850 | -122.66038 | Adit | False |

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


**Bohemia district** (Bulletin 61 p. 309-317; Lane County, Ts. 22-23 S., Rs. 1-2 E.).
Discovered 1858 (Oglesby & Brass); gold found near the head of City Creek in 1863
by Bohemia Johnson and George Ramsey, triggering the district's main rush. By 1902
more than 2,000 claims had been filed (many duplicates). Main producers: Champion,
Helena, and Musick mines, with lesser output from Noonday, Vesuvius, and Star.
District total production is estimated at **about $1,000,000**; separately, Lane
County (mainly Bohemia) produced 14,590.69 oz gold + 1,418.79 oz silver 1880-1900
per U.S. Mint records, and 13,694.59 oz gold (from 42,548 tons crude ore) 1901-1930
per USBM records (p. 311).

**Caveat:** Bulletin 61's Bohemia coverage is almost entirely about hard-rock LODE
mines (quartz veins with sphalerite/galena/chalcopyrite/pyrite) draining into Brice,
Sharps, and Steamboat Creeks -- it does not separately describe placer bars/benches
on Sharps, Brice, Martin, or Quartz Creek by name. Placer gold in these creeks is
consistent with erosion of the district's many lode workings, but the bulletin gives
no placer-specific production figures for them. Bibliography includes Bales, W.E.,
1951, "Geology of the lower Brice Creek area, Lane County, Oregon" (Univ. Oregon
thesis) -- not independently reviewed for this build.

**OHMI (Lane County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-lane.aspx

