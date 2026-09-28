# quartzville -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-122.5, 44.48, -122.15, 44.68)`
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
2. After import, select all the newly-imported items -> **Add to folder** -> name it `"quartzville <layer>"` (e.g. `"quartzville 1_my_claims"`).
3. Repeat per layer file. Each file is small and single-purpose so the folder step stays quick.

## Output files
- `quartzville_1_my_claims.gpx` (+ `quartzville_1_my_claims.kml` secondary) -- 4 items, 3.4 KB GPX [OK]
- `quartzville_3_other_claims.gpx` (+ `quartzville_3_other_claims.kml` secondary) -- 48 items, 43.9 KB GPX [OK]
- `quartzville_4_history.gpx` (+ `quartzville_4_history.kml` secondary) -- 121 items, 28.3 KB GPX [OK]
- `quartzville_5_scout.gpx` (+ `quartzville_5_scout.kml` secondary) -- 10 items, 3.1 KB GPX [OK]
- `caltopo_quartzville.geojson` -- CalTopo bundle, 183 features, all layers combined

## Layer counts
- 1_my_claims: 4
- 2_public: 0 (no verified public-corridor extent geometry source in this build -- not rendered rather than invented)
- 3_other_claims: 48 (excluded as ours: 2, clipped to bbox: 1)
- 4_history: 121 / 150 cap (raw records: 246, clusters before cap: 121, dropped generic MILO far from USMIN: 0, dropped prospect pits over cap: 0)
- 5_scout: 10 / 10 cap (candidate pool: 25, NHD stream filter skipped: False, land checks: {'public_confirmed': 10, 'private_dropped': 0, 'unverifiable': 0})
- 6_access: 0 (no club handbook / access-directions source data exists in this repo -- skipped rather than inventing a route)

## My claims (layer 1) resolution detail
- **WVM 1B Dry Gulch** -- area+pin (WVM #1  B)
- **Cedar Bend Placer** -- area+pin (CEDAR BEND)

## Caveats specific to this area
- BLM claim polygons are approximate to the quarter-section (not drawn from a legal survey).
- Layer 1 'directions' field: no club handbook source exists in this repo, so it reads 'not available' rather than being invented.
- Layer 2 public-corridor Areas are skipped (no verified extent-polygon source) -- only point pins are rendered for public sites.
- Layer 5 scout candidates' final tiebreaker is distance-to-stream, not distance-to-road (no road dataset fetched in this build).
- Layer 6 access routes: skipped, no handbook/directions source data exists in this repo.
- MRDS attribute detail is limited to what its public WFS exposes (name/status/commodity codes).

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

