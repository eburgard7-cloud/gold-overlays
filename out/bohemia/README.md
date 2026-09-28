# bohemia -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-122.95, 43.45, -122.5, 43.78)`
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
2. After import, select all the newly-imported items -> **Add to folder** -> name it `"bohemia <layer>"` (e.g. `"bohemia 1_my_claims"`).
3. Repeat per layer file. Each file is small and single-purpose so the folder step stays quick.

## Output files
- `bohemia_1_my_claims.gpx` (+ `bohemia_1_my_claims.kml` secondary) -- 18 items, 10.2 KB GPX [OK]
- `bohemia_2_public.gpx` (+ `bohemia_2_public.kml` secondary) -- 1 items, 0.6 KB GPX [OK]
- `bohemia_3_other_claims.gpx` (+ `bohemia_3_other_claims.kml` secondary) -- 138 items, 98.3 KB GPX [OK]
- `bohemia_4_history.gpx` (+ `bohemia_4_history.kml` secondary) -- 150 items, 34.4 KB GPX [OK]
- `bohemia_5_scout.gpx` (+ `bohemia_5_scout.kml` secondary) -- 10 items, 3.2 KB GPX [OK]
- `caltopo_bohemia.geojson` -- CalTopo bundle, 317 features, all layers combined

## Layer counts
- 1_my_claims: 18
- 2_public: 1 (no verified public-corridor extent geometry source in this build -- not rendered rather than invented)
- 3_other_claims: 138 (excluded as ours: 9, clipped to bbox: 6)
- 4_history: 150 / 150 cap (raw records: 1182, clusters before cap: 676, dropped generic MILO far from USMIN: 0, dropped prospect pits over cap: 1)
- 5_scout: 10 / 10 cap (candidate pool: 25, NHD stream filter skipped: False, land checks: {'public_confirmed': 10, 'private_dropped': 0, 'unverifiable': 0})
- 6_access: 0 (no club handbook / access-directions source data exists in this repo -- skipped rather than inventing a route)

## My claims (layer 1) resolution detail
- **BMOA War Eagle III** -- area+pin (WAR EAGLE III)
- **BMOA Westside** -- area+pin (WESTSIDE)
- **BMOA Y Not** -- area+pin (Y NOT)
- **BMOA Placer Claim** -- area+pin (PLACER CLAIM)
- **BMOA Little Red** -- area+pin (LITTLE RED)
- **BMOA Big Bend** -- area+pin (BIG BEND)
- **BMOA Argentite** -- area+pin (ARGENTITE)
- **BMOA Exodus** -- area+pin (EXODUS)
- **BMOA 4 Aces** -- area+pin (4 ACES)

## Caveats specific to this area
- BLM claim polygons are approximate to the quarter-section (not drawn from a legal survey).
- Layer 1 'directions' field: no club handbook source exists in this repo, so it reads 'not available' rather than being invented.
- Layer 2 public-corridor Areas are skipped (no verified extent-polygon source) -- only point pins are rendered for public sites.
- Layer 5 scout candidates' final tiebreaker is distance-to-stream, not distance-to-road (no road dataset fetched in this build).
- Layer 6 access routes: skipped, no handbook/directions source data exists in this repo.
- MRDS attribute detail is limited to what its public WFS exposes (name/status/commodity codes).

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

