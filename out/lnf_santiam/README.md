# lnf_santiam -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-122.62, 44.75, -122.4, 44.86)`
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
2. After import, select all the newly-imported items -> **Add to folder** -> name it `"lnf_santiam <layer>"` (e.g. `"lnf_santiam 1_my_claims"`).
3. Repeat per layer file. Each file is small and single-purpose so the folder step stays quick.

## Output files
- `lnf_santiam_1_my_claims.gpx` (+ `lnf_santiam_1_my_claims.kml` secondary) -- 1 items, 0.7 KB GPX [OK]
- `lnf_santiam_3_other_claims.gpx` (+ `lnf_santiam_3_other_claims.kml` secondary) -- 5 items, 4.4 KB GPX [OK]
- `caltopo_lnf_santiam.geojson` -- CalTopo bundle, 6 features, all layers combined

## Layer counts
- 1_my_claims: 1
- 2_public: 0 (no verified public-corridor extent geometry source in this build -- not rendered rather than invented)
- 3_other_claims: 5 (excluded as ours: 0, clipped to bbox: 0)
- 4_history: 0 / 150 cap (raw records: 0, clusters before cap: 0, dropped generic MILO far from USMIN: 0, dropped prospect pits over cap: 0)
- 5_scout: 0 / 10 cap (candidate pool: 0, NHD stream filter skipped: False, land checks: {'public_confirmed': 0, 'private_dropped': 0, 'unverifiable': 0})
- 6_access: 0 (no club handbook / access-directions source data exists in this repo -- skipped rather than inventing a route)

## My claims (layer 1) resolution detail
- **WVM-LNF25 Little North Santiam** -- pin-only (no MLRS polygon)

## Caveats specific to this area
- BLM claim polygons are approximate to the quarter-section (not drawn from a legal survey).
- Layer 1 'directions' field: no club handbook source exists in this repo, so it reads 'not available' rather than being invented.
- Layer 2 public-corridor Areas are skipped (no verified extent-polygon source) -- only point pins are rendered for public sites.
- Layer 5 scout candidates' final tiebreaker is distance-to-stream, not distance-to-road (no road dataset fetched in this build).
- Layer 6 access routes: skipped, no handbook/directions source data exists in this repo.
- MRDS attribute detail is limited to what its public WFS exposes (name/status/commodity codes).

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

