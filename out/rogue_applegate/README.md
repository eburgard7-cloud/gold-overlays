# rogue_applegate -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-123.65, 42.15, -122.85, 42.7)`
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
2. After import, select all the newly-imported items -> **Add to folder** -> name it `"rogue_applegate <layer>"` (e.g. `"rogue_applegate 1_my_claims"`).
3. Repeat per layer file. Each file is small and single-purpose so the folder step stays quick.

## Output files
- `rogue_applegate_3_other_claims.gpx` (+ `rogue_applegate_3_other_claims.kml` secondary) -- 751 items, 592.7 KB GPX [OK]
- `rogue_applegate_4_history.gpx` (+ `rogue_applegate_4_history.kml` secondary) -- 150 items, 35.7 KB GPX [OK]
- `rogue_applegate_5_scout.gpx` (+ `rogue_applegate_5_scout.kml` secondary) -- 10 items, 3.1 KB GPX [OK]
- `caltopo_rogue_applegate.geojson` -- CalTopo bundle, 911 features, all layers combined

## Layer counts
- 1_my_claims: 0
- 2_public: 0 (no verified public-corridor extent geometry source in this build -- not rendered rather than invented)
- 3_other_claims: 751 (excluded as ours: 0, clipped to bbox: 94)
- 4_history: 150 / 150 cap (raw records: 1653, clusters before cap: 942, dropped generic MILO far from USMIN: 0, dropped prospect pits over cap: 126)
- 5_scout: 10 / 10 cap (candidate pool: 25, NHD stream filter skipped: False, land checks: {'public_confirmed': 10, 'private_dropped': 0, 'unverifiable': 0})
- 6_access: 0 (no club handbook / access-directions source data exists in this repo -- skipped rather than inventing a route)

## My claims (layer 1) resolution detail

## Caveats specific to this area
- BLM claim polygons are approximate to the quarter-section (not drawn from a legal survey).
- Layer 1 'directions' field: no club handbook source exists in this repo, so it reads 'not available' rather than being invented.
- Layer 2 public-corridor Areas are skipped (no verified extent-polygon source) -- only point pins are rendered for public sites.
- Layer 5 scout candidates' final tiebreaker is distance-to-stream, not distance-to-road (no road dataset fetched in this build).
- Layer 6 access routes: skipped, no handbook/directions source data exists in this repo.
- MRDS attribute detail is limited to what its public WFS exposes (name/status/commodity codes).

## DOGAMI Bulletin 61 notes


**Klamath Mountains regional placer history** (Bulletin 61 p. 167-169) covers this
area's context directly: Oregon's first documented placer gold find was 1850 on the
Illinois River near Josephine Creek; the district-defining 1851 rush was **near
Jacksonville**. Richer placers named include **Sterling Creek** (>$3,000,000,
fed the 23-mile Sterling ditch off the **Little Applegate River**, built 1877),
Althouse Creek, Sailors Diggings, Rich Gulch (Jacksonville) and **Rich Gulch at
Galice**. Placers are also named on Sucker, Josephine, Briggs, **Galice**, **Grave
Creek and its tributaries**, Foots, Sardine, Galls, Forest, Poorman, Humbug, Ferris
Gulch, Powell, and Palmer Creeks. The **Old Channel placer mine near Galice** is
called one of the largest hydraulic operations in the U.S. (peak crew 75 in 1935).
Dredging is documented on Foots Creek (1903, one of Oregon's first dredges, later
electrified from the Gold Hill hydro plant), and on the **Rogue River near Gold
Hill** and near the town of Rogue River, and on the **Applegate River near Ruch**
(p. 169).

**Galice area / Silver Peak lode context** (p. 208-214) documents the Big Yank lode
trend from the Almeda mine (Galice) north to the Silver Peak mine near Canyonville
-- outside this box but geologically related.

**Caveat:** Bulletin 61 does not give a single consolidated production figure for
"the Rogue/Applegate district" as a unit -- figures above are per-creek/per-mine as
cited. Gold Hill waysides and the Grave Creek confluence area are covered by the
general narrative above rather than a dedicated sub-section.

**OHMI (Jackson County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-jackson.aspx -- **(Josephine County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-josephine.aspx

