# calapooia -- gold-overlay build report

Bounding box (WGS84 minLon,minLat,maxLon,maxLat): `(-122.55, 44.15, -122.28, 44.32)`
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
2. After import, select all the newly-imported items -> **Add to folder** -> name it `"calapooia <layer>"` (e.g. `"calapooia 1_my_claims"`).
3. Repeat per layer file. Each file is small and single-purpose so the folder step stays quick.

## Output files
- `calapooia_1_my_claims.gpx` (+ `calapooia_1_my_claims.kml` secondary) -- 2 items, 1.5 KB GPX [OK]
- `calapooia_3_other_claims.gpx` (+ `calapooia_3_other_claims.kml` secondary) -- 20 items, 13.9 KB GPX [OK]
- `calapooia_4_history.gpx` (+ `calapooia_4_history.kml` secondary) -- 150 items, 35.1 KB GPX [OK]
- `calapooia_5_scout.gpx` (+ `calapooia_5_scout.kml` secondary) -- 9 items, 2.8 KB GPX [OK]
- `caltopo_calapooia.geojson` -- CalTopo bundle, 181 features, all layers combined

## Layer counts
- 1_my_claims: 2
- 2_public: 0 (no verified public-corridor extent geometry source in this build -- not rendered rather than invented)
- 3_other_claims: 20 (excluded as ours: 1, clipped to bbox: 1)
- 4_history: 150 / 150 cap (raw records: 296, clusters before cap: 169, dropped generic MILO far from USMIN: 0, dropped prospect pits over cap: 0)
- 5_scout: 9 / 10 cap (candidate pool: 25, NHD stream filter skipped: False, land checks: {'public_confirmed': 9, 'private_dropped': 0, 'unverifiable': 0})
- 6_access: 0 (no club handbook / access-directions source data exists in this repo -- skipped rather than inventing a route)

## My claims (layer 1) resolution detail
- **Golden Dollar** -- area+pin (GOLDEN DOLLAR)

## Caveats specific to this area
- BLM claim polygons are approximate to the quarter-section (not drawn from a legal survey).
- Layer 1 'directions' field: no club handbook source exists in this repo, so it reads 'not available' rather than being invented.
- Layer 2 public-corridor Areas are skipped (no verified extent-polygon source) -- only point pins are rendered for public sites.
- Layer 5 scout candidates' final tiebreaker is distance-to-stream, not distance-to-road (no road dataset fetched in this build).
- Layer 6 access routes: skipped, no handbook/directions source data exists in this repo.
- MRDS attribute detail is limited to what its public WFS exposes (name/status/commodity codes).

## DOGAMI Bulletin 61 notes


**Blue River district** (Bulletin 61 p. 299-306; southern Linn / northern Lane
County, Ts. 15-16 S., R. 4 E., straddling the Calapooia/McKenzie drainage divide).
Bulletin 61 does not have a separate "Calapooia" district -- the upper Calapooia
River headwaters fall within the area the bulletin treats as the Blue River
district. Principal mine: **Lucky Boy** (reached via a road up Quartz Creek from
the town of Blue River), with lesser prospects Cinderella, Great Northern, Poorman,
Rowena, Tate, Treasurer, Union. Veins carry pyrite/sphalerite/galena/chalcopyrite in
a quartz gangue, with calcite locally dominant (Great Northern, Higgins, Cinderella).
Western Cascades total production (combining Blue River + Fall Creek + other minor
districts, not separated out) is given as **about $1.5 million** (p. 306, 15373 in
the OCR text).

**Caveat:** no placer-specific content or named bars/benches for the Calapooia River
itself were found in Bulletin 61 -- treat this area's placer potential as inferred
from lode erosion, not from any documented placer history.

**OHMI (Linn County):** https://www.oregon.gov/dogami/milo/Pages/ohmi-linn.aspx

