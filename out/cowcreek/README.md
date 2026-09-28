# cowcreek -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-123.7, 42.68, -123.1, 42.98)`
Built: 2026-09-28

## Legend

| layer | icon | color | style | meaning |
|---|---|---|---|---|
| 1_my_claims | Mineral Site (pin) / filled Area | yellow | solid | WVM/BMOA club claims -- ours |
| 2_public | Location (pin) | black | n/a (points only) | Public gold-panning sites open to anyone |
| 3_other_claims | Area only, no pins | red | dotted | Other active BLM claims -- don't dig here |
| 4_history | Mineral Site (placer/tailings/hydraulic) / Location (adit/shaft/pit) | black | n/a (points only) | Deduped historical workings |
| 5_scout | Location (pin) | red | n/a (points only) | Open-ground candidates worth scouting |
| 6_access | Line | black | dash/dot | Claim-access route (only where a real source describes one) |

Only confirmed onX icons/colors are used: icons `Mineral Site` / `Location`; colors yellow `rgba(255,255,0,1)`, red `rgba(255,51,0,1)`, black `rgba(0,0,0,1)`. Green for confirmed public sites and any other icon/color in `onx_samples/onx_test.gpx` is a GUESS pending `onx_samples/STYLE_RESULTS.md` -- not used until confirmed (see top-level README).

## Import steps (phone)

1. onX app -> **My Content** -> **Import** -> choose one `<area>_<layer>.gpx` file.
2. After import, select all the newly-imported items -> **Add to folder** -> name it `"cowcreek <layer>"` (e.g. `"cowcreek 1_my_claims"`).
3. Repeat per layer file. Each file is small and single-purpose so the folder step stays quick.

## Output files
- `cowcreek_1_my_claims.gpx` (+ `cowcreek_1_my_claims.kml` secondary) -- 8 items, 5.0 KB GPX [OK]
- `cowcreek_2_public.gpx` (+ `cowcreek_2_public.kml` secondary) -- 1 items, 0.6 KB GPX [OK]
- `cowcreek_3_other_claims.gpx` (+ `cowcreek_3_other_claims.kml` secondary) -- 203 items, 149.0 KB GPX [OK]
- `cowcreek_4_history.gpx` (+ `cowcreek_4_history.kml` secondary) -- 150 items, 34.7 KB GPX [OK]
- `cowcreek_5_scout.gpx` (+ `cowcreek_5_scout.kml` secondary) -- 10 items, 3.0 KB GPX [OK]
- `caltopo_cowcreek.geojson` -- CalTopo bundle, 372 features, all layers combined

## Layer counts
- 1_my_claims: 8
- 2_public: 1 (no verified public-corridor extent geometry source in this build -- not rendered rather than invented)
- 3_other_claims: 203 (excluded as ours: 4, clipped to bbox: 30)
- 4_history: 150 / 150 cap (raw records: 430, clusters before cap: 231, dropped generic MILO far from USMIN: 0, dropped prospect pits over cap: 47)
- 5_scout: 10 / 10 cap (candidate pool: 25, NHD stream filter skipped: False, land checks: {'public_confirmed': 10, 'private_dropped': 0, 'unverifiable': 0})
- 6_access: 0 (no club handbook / access-directions source data exists in this repo -- skipped rather than inventing a route)

## My claims (layer 1) resolution detail
- **WVM 3 Dads Creek** -- area+pin (WVM #3)
- **WVM 4 Dads Creek** -- area+pin (WVM #4)
- **WVM 5 Dads Creek** -- area+pin (WVM #5)
- **Pure White Gold (Whitehorse Cr)** -- area+pin (PURE WHITE GOLD)

## Caveats specific to this area
- BLM claim polygons are approximate to the quarter-section (not drawn from a legal survey).
- Layer 1 'directions' field: no club handbook source exists in this repo, so it reads 'not available' rather than being invented.
- Layer 2 public-corridor Areas are skipped (no verified extent-polygon source) -- only point pins are rendered for public sites.
- Layer 5 scout candidates' final tiebreaker is distance-to-stream, not distance-to-road (no road dataset fetched in this build).
- Layer 6 access routes: skipped, no handbook/directions source data exists in this repo.
- MRDS attribute detail is limited to what its public WFS exposes (name/status/commodity codes).

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

